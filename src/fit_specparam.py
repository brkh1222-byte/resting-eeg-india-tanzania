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

Run:  .venv/bin/python src/fit_specparam.py [--jobs 6] [--no-grid]
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
    """Alpha, theta and aperiodic features from a fitted model."""
    if fm is None:
        return {"fit_ok": False}
    ap = fm.aperiodic_params_
    out = {"fit_ok": True, "offset": ap[0], "exponent": ap[-1],
           "knee": ap[1] if len(ap) == 3 else np.nan,
           "r2": fm.r_squared_, "fit_error": fm.error_}
    peaks = fm.peak_params_ if fm.peak_params_.size else np.empty((0, 3))
    a = peaks[(peaks[:, 0] >= band[0]) & (peaks[:, 0] <= band[1])]
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


def process_one(args) -> dict | list:
    pid, task, grid = args
    z = np.load(C.DERIV / "psd" / f"{pid}_{task}.npz")
    freqs, psd, names = z["freqs"], z["psd"].astype(float), list(z["ch_names"])
    row = {"participant_id": pid, "task": task}
    spec = roi_spectrum(psd, names, C.ROI_PRIMARY)
    fm = fit_one(freqs, spec)
    row.update(features(fm))
    row["sg_present"], row["sg_iaf"] = sg_detect(freqs, spec)
    row["raw_peak_7_12"] = float(freqs[(freqs >= 7) & (freqs <= 12)][np.argmax(spec[(freqs >= 7) & (freqs <= 12)])])
    row["_fm_flat"] = None
    grid_rows = []
    if grid and task == "ec":
        rois = {"O1O2": roi_spectrum(psd, names, C.ROI_PRIMARY),
                "posterior4": roi_spectrum(psd, names, C.ROI_POSTERIOR4)}
        post = [c for c in POSTERIOR if c in names]
        for fr, mode, h in itertools.product(C.GRID["fit_range"], C.GRID["aperiodic_mode"],
                                             C.GRID["min_peak_height"]):
            base = {"participant_id": pid, "fit_range": f"{fr[0]:g}-{fr[1]:g}", "mode": mode,
                    "min_peak_height": h}
            for roi, s in rois.items():
                if s is None:
                    continue
                g = features(fit_one(freqs, s, fr, mode, h))
                grid_rows.append({**base, "roi": roi, **{k: g.get(k) for k in
                                  ("fit_ok", "alpha_present", "iaf", "alpha_pw", "exponent", "r2")}})
            # "any posterior channel": present if any single posterior channel has a peak
            per = [features(fit_one(freqs, psd[names.index(c)], fr, mode, h)) for c in post]
            per = [p for p in per if p.get("fit_ok")]
            if per:
                pres = [p for p in per if p["alpha_present"]]
                top = max(pres, key=lambda p: p["alpha_pw"]) if pres else None
                grid_rows.append({**base, "roi": "any_posterior", "fit_ok": True,
                                  "alpha_present": bool(pres),
                                  "iaf": top["iaf"] if top else np.nan,
                                  "alpha_pw": top["alpha_pw"] if top else np.nan,
                                  "exponent": float(np.mean([p["exponent"] for p in per])),
                                  "r2": float(np.min([p["r2"] for p in per]))})
    return row, grid_rows, (freqs, spec, fm.aperiodic_params_ if fm else None)


def main() -> None:
    from prereg_guard import require_prereg
    print("Pre-registration commit:", require_prereg())
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--no-grid", action="store_true")
    args = ap.parse_args()

    files = sorted((C.DERIV / "psd").glob("*.npz"))
    jobs = [(f.stem.rsplit("_", 1)[0], f.stem.rsplit("_", 1)[1], not args.no_grid) for f in files]
    rows, grid = [], []
    with ProcessPoolExecutor(args.jobs) as pool:
        for row, g, _ in pool.map(process_one, jobs, chunksize=2):
            row.pop("_fm_flat", None)
            rows.append(row)
            grid.extend(g)
    feats = pd.DataFrame(rows)

    # Reactivity: 1/f-removed power around the eyes-closed IAF (7-14 Hz centre 10.5 if no EC peak)
    react = []
    for pid, g in feats.groupby("participant_id"):
        if set(g["task"]) != {"ec", "eo"}:
            continue
        ec = g[g["task"] == "ec"].iloc[0]
        centre = ec["iaf"] if ec["alpha_present"] else float(np.mean(C.ALPHA_BAND))
        vals = {}
        for task in ("ec", "eo"):
            z = np.load(C.DERIV / "psd" / f"{pid}_{task}.npz")
            spec = roi_spectrum(z["psd"].astype(float), list(z["ch_names"]), C.ROI_PRIMARY)
            vals[task] = flat_power(fit_one(z["freqs"], spec), centre)
        react.append({"participant_id": pid, "reactivity_log10": vals["ec"] - vals["eo"]})
    feats = feats.merge(pd.DataFrame(react), on="participant_id", how="left")

    feats.to_csv(C.RESULTS / "features.csv", index=False)
    pd.DataFrame(grid).to_csv(C.RESULTS / "features_grid.csv", index=False)
    feats.loc[~feats["fit_ok"], ["participant_id", "task"]].to_csv(C.RESULTS / "fit_failures.csv", index=False)
    print(feats.groupby("task")[["fit_ok", "alpha_present", "sg_present"]].mean())


if __name__ == "__main__":
    main()
