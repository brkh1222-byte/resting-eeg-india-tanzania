"""Fit specparam (FOOOF 1.1) to every spectrum and extract the outcome features.

PRIMARY features (one row per participant x task), region = mean of O1 and O2:
  alpha_present  any peak with centre 7-14 Hz and height >= 0.1 log10 above the 1/f fit
  iaf            centre frequency of the tallest such peak (Hz)
  alpha_pw       its height above the 1/f fit (log10 power)
  alpha_bw       its width (Hz)
  exponent, offset   aperiodic fit
  theta_present, theta_cf
  r2, fit_error
  sg_present, sg_iaf   second detector (see sg_detect)
  alpha_flat_mean  mean 1/f-removed power in IAF +/- 2 Hz (for reactivity)

ROBUSTNESS grid (eyes closed only): every combination in config.GRID,
written to results/features_grid.csv.

Blocked until the pre-registration is committed.

Run:  .venv/bin/python src/fit_specparam.py [--jobs 2] [--no-grid]
Outputs: results/features.csv, results/features_grid.csv, results/fit_failures.csv
"""
import argparse
import itertools
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

warnings.filterwarnings("ignore")
POSTERIOR = ["O1", "O2", "P7", "P8", "P3", "P4", "P5", "P6", "PO7", "PO8", "O9", "O10", "Oz", "Pz"]


def fit_one(freqs, spectrum, fit_range=C.FIT_RANGE, mode=C.APERIODIC_MODE,
            min_height=C.MIN_PEAK_HEIGHT):
    """Fit one spectrum. Returns the FOOOF object, or None if the fit failed."""
    from fooof import FOOOF
    fm = FOOOF(peak_width_limits=list(C.PEAK_WIDTH_LIMITS), max_n_peaks=C.MAX_N_PEAKS,
               min_peak_height=min_height, peak_threshold=C.PEAK_THRESHOLD,
               aperiodic_mode=mode, verbose=False)
    try:
        fm.fit(freqs, spectrum, list(fit_range))
    except Exception:
        return None
    return fm if fm.has_model else None


def features(fm, band=C.ALPHA_BAND) -> dict:
    """Alpha, theta and aperiodic features from a fitted model.

    A failed fit returns fit_ok=False and alpha_present=False, so that it is
    counted as "no peak detected" in H1 and H2 (prereg section 4.5: poor fits
    must not be quietly removed from the "absent" group). Failures are listed
    in results/fit_failures.csv.
    """
    if fm is None:
        return {"fit_ok": False, "alpha_present": False, "n_alpha_peaks": 0,
                "theta_present": False}
    ap = fm.aperiodic_params_
    out = {"fit_ok": True, "offset": ap[0], "exponent": ap[-1],
           "knee": ap[1] if len(ap) == 3 else np.nan,
           "r2": fm.r_squared_, "fit_error": fm.error_}
    peaks = fm.peak_params_ if fm.peak_params_.size else np.empty((0, 3))
    a = peaks[(peaks[:, 0] >= band[0]) & (peaks[:, 0] <= band[1])]
    if C.PRESENCE_MIN_FITTED_HEIGHT is not None:
        a = a[a[:, 1] >= C.PRESENCE_MIN_FITTED_HEIGHT]
    out["alpha_present"] = bool(len(a))
    out["n_alpha_peaks"] = int(len(a))
    if len(a):
        best = a[np.argmax(a[:, 1])]
        out.update(iaf=best[0], alpha_pw=best[1], alpha_bw=best[2])
    else:
        out.update(iaf=np.nan, alpha_pw=np.nan, alpha_bw=np.nan)
    t = peaks[(peaks[:, 0] >= C.THETA_BAND[0]) & (peaks[:, 0] < C.THETA_BAND[1])]
    out["theta_present"] = bool(len(t))
    out["theta_cf"] = t[np.argmax(t[:, 1]), 0] if len(t) else np.nan
    return out


def flat_power(fm, centre: float) -> float:
    """Mean 1/f-removed log10 power within centre +/- 2 Hz."""
    if fm is None:
        return np.nan
    lo, hi = centre - C.REACTIVITY_HALF_WIDTH, centre + C.REACTIVITY_HALF_WIDTH
    m = (fm.freqs >= lo) & (fm.freqs <= hi)
    return float(fm._spectrum_flat[m].mean())


def sg_detect(freqs, spectrum, band=C.ALPHA_BAND) -> tuple[bool, float]:
    """Second, simpler detector adapted from the restingIAF idea (Corcoran et al., 2018).

    Smooth log10 power with a Savitzky-Golay filter (11 bins = 2.75 Hz, order 5),
    find local maxima in the alpha window, and accept the one that rises most above
    a straight-line fit of log-power on log-frequency (2-40 Hz) if that rise exceeds
    both 2 SD of the residuals outside the alpha window and 0.05 log10 (about 12%).
    This is our adaptation, not the official restingIAF package.
    """
    m = (freqs >= 2) & (freqs <= 40)
    f, lp = freqs[m], np.log10(spectrum[m])
    sm = savgol_filter(lp, 11, 5)
    coef = np.polyfit(np.log10(f), lp, 1)
    resid = sm - np.polyval(coef, np.log10(f))
    d = np.diff(sm)
    idx = np.where((d[:-1] > 0) & (d[1:] <= 0))[0] + 1
    idx = idx[(f[idx] >= band[0]) & (f[idx] <= band[1])]
    if not len(idx):
        return False, np.nan
    best = idx[np.argmax(resid[idx])]
    outside = (f < band[0] - 1) | (f > band[1] + 1)
    ok = resid[best] > max(2 * resid[outside].std(), 0.05)
    return bool(ok), float(f[best]) if ok else np.nan


def roi_spectrum(psd, ch_names, chans):
    idx = [list(ch_names).index(c) for c in chans if c in ch_names]
    if len(idx) < len(chans):
        return None
    return psd[idx].mean(axis=0)


def raw_peak(freqs, spec, lo=7.0, hi=12.0) -> float:
    """Tallest point of the raw spectrum in 7-12 Hz (the Vianney et al., 2025 approach)."""
    m = (freqs >= lo) & (freqs <= hi)
    return float(freqs[m][np.argmax(spec[m])])


def load_psd(pid: str, task: str):
    z = np.load(C.DERIV / "psd" / f"{pid}_{task}.npz")
    return z["freqs"], z["psd"].astype(float), [str(c) for c in z["ch_names"]]


def grid_rows_for(pid: str, freqs, psd, names) -> list[dict]:
    """All robustness-grid fits for one eyes-closed recording (R^2 floors are applied later)."""
    rows = []
    rois = {"O1O2": roi_spectrum(psd, names, C.ROI_PRIMARY),
            "posterior4": roi_spectrum(psd, names, C.ROI_POSTERIOR4)}
    post = [c for c in POSTERIOR if c in names]
    cols = ("fit_ok", "alpha_present", "iaf", "alpha_pw", "exponent", "r2")
    for fr, mode, h in itertools.product(C.GRID["fit_range"], C.GRID["aperiodic_mode"],
                                         C.GRID["min_peak_height"]):
        base = {"participant_id": pid, "fit_range": f"{fr[0]:g}-{fr[1]:g}", "mode": mode,
                "min_peak_height": h}
        for roi, s in rois.items():
            if s is None:
                continue
            g = features(fit_one(freqs, s, fr, mode, h))
            rows.append({**base, "roi": roi, **{k: g.get(k, np.nan) for k in cols}})
        # "any posterior channel": present if any single posterior channel has a peak
        per = [features(fit_one(freqs, psd[names.index(c)], fr, mode, h)) for c in post]
        per = [p for p in per if p.get("fit_ok")]
        if per:
            pres = [p for p in per if p["alpha_present"]]
            top = max(pres, key=lambda p: p["alpha_pw"]) if pres else None
            rows.append({**base, "roi": "any_posterior", "fit_ok": True,
                         "alpha_present": bool(pres),
                         "iaf": top["iaf"] if top else np.nan,
                         "alpha_pw": top["alpha_pw"] if top else np.nan,
                         "exponent": float(np.mean([p["exponent"] for p in per])),
                         "r2": float(np.min([p["r2"] for p in per]))})
    return rows


def process_participant(args) -> tuple[list[dict], list[dict]]:
    """All primary features (and the grid) for one participant.

    Returns (feature rows, one per task; grid rows). Errors are returned as rows
    with fit_ok=False and an error message, and never stop the run.
    """
    pid, tasks, grid = args
    rows, grid_rows, fits = [], [], {}
    for task in tasks:
        row = {"participant_id": pid, "task": task}
        try:
            freqs, psd, names = load_psd(pid, task)
            spec = roi_spectrum(psd, names, C.ROI_PRIMARY)
            if spec is None:
                raise ValueError("O1 or O2 missing from the saved spectrum")
            fm = fit_one(freqs, spec)
            fits[task] = fm
            row.update(features(fm))
            row["sg_present"], row["sg_iaf"] = sg_detect(freqs, spec)
            row["raw_peak_7_12"] = raw_peak(freqs, spec)
            if grid and task == "ec":
                grid_rows = grid_rows_for(pid, freqs, psd, names)
        except Exception as exc:
            row.update(features(None), error=str(exc))
        rows.append(row)
    # Reactivity: 1/f-removed power around the eyes-closed IAF, eyes closed minus eyes open,
    # each condition fitted separately. No eyes-closed peak -> window centred on 10.5 Hz.
    if fits.get("ec") is not None and fits.get("eo") is not None:
        ec = rows[list(tasks).index("ec")]
        centre = ec["iaf"] if ec["alpha_present"] else float(np.mean(C.ALPHA_BAND))
        react = flat_power(fits["ec"], centre) - flat_power(fits["eo"], centre)
        for r in rows:
            r["reactivity_log10"] = react
    return rows, grid_rows


def run(jobs: int = 2, grid: bool = True) -> tuple[pd.DataFrame, pd.DataFrame]:
    files = sorted((C.DERIV / "psd").glob("*.npz"))
    by_pid: dict[str, list[str]] = {}
    for f in files:
        pid, task = f.stem.rsplit("_", 1)
        by_pid.setdefault(pid, []).append(task)
    jobs_list = [(pid, sorted(tasks), grid) for pid, tasks in sorted(by_pid.items())]
    rows, grid_rows = [], []
    if jobs == 1:
        results = map(process_participant, jobs_list)
    else:
        pool = ProcessPoolExecutor(jobs)
        results = pool.map(process_participant, jobs_list, chunksize=2)
    for r, g in results:
        rows.extend(r)
        grid_rows.extend(g)
    feats = pd.DataFrame(rows)
    if "error" not in feats:
        feats["error"] = np.nan
    feats.to_csv(C.RESULTS / "features.csv", index=False)
    grid_df = pd.DataFrame(grid_rows)
    if grid:
        grid_df.to_csv(C.RESULTS / "features_grid.csv", index=False)
    feats.loc[~feats["fit_ok"].astype(bool), ["participant_id", "task", "error"]].to_csv(
        C.RESULTS / "fit_failures.csv", index=False)
    return feats, grid_df


def main() -> None:
    from prereg_guard import require_prereg
    print("Pre-registration commit:", require_prereg())
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--no-grid", action="store_true")
    args = ap.parse_args()
    feats, _ = run(args.jobs, not args.no_grid)
    print(feats.groupby("task")[["fit_ok", "alpha_present", "sg_present"]].mean())


if __name__ == "__main__":
    main()
