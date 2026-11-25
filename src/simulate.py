"""Simulated recordings with known ground truth, to validate the pipeline.

Nothing here touches the real data. A simulated recording is a Gaussian time
series at the headset's sampling rate (128 Hz) whose spectrum is known exactly:

    log10 P(f) = offset - exponent * log10(f) + alpha_height * exp(-(f - cf)^2 / (2 sd^2))

i.e. a 1/f ("aperiodic") background plus an optional alpha peak whose height is
given in log10 units above the background, the same quantity that specparam
reports and that the pre-registration thresholds at 0.1. Optional extras: 50 Hz
line noise, a white sensor-noise floor, a hardware-like low-pass, intermittent
(bursty) alpha, artefact epochs and other peaks.

Each simulated recording goes through the SAME functions as the real data:
preprocess.prepare (1-45 Hz filter), preprocess.accepted_epochs (4 s epochs,
rejection), psd.epoch_spectra (median Welch) and fit_specparam.fit_one /
features / sg_detect.

Commands
  .venv/bin/python src/simulate.py experiments --out DIR [--n 200] [--only A,B]
      Monte-Carlo experiments A-J (see EXPERIMENTS); one CSV each; re-runnable.
  .venv/bin/python src/simulate.py cohort --root DIR [--n-per-site 300] [--no-grid]
      Build a simulated two-site cohort with planted effects in DIR (outside the
      repository or under the git-ignored data/sim/), run fit_specparam, models, robustness and figures on it, and
      write DIR/results/recovery.csv comparing estimates with the planted truth.
"""
import argparse
import itertools
import json
import os
import subprocess
import sys
import time
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

warnings.filterwarnings("ignore")
SFREQ = 128.0


# ------------------------------------------------------------------ ground truth
@dataclass
class Truth:
    exponent: float = 1.2
    offset: float = 1.0               # log10 uV^2/Hz at 1 Hz
    alpha_height: float = 0.4         # log10 above the 1/f background; 0 = no alpha
    alpha_cf: float = 10.0            # Hz
    alpha_sd: float = 1.0             # Hz (specparam bandwidth = 2 x sd)
    extra_peaks: tuple = ()           # ((cf, height, sd), ...), e.g. theta or beta
    floor_cross_hz: float | None = None   # white sensor noise as strong as the 1/f at this frequency
    line_uv: float = 0.0              # amplitude of a 50 Hz sinusoid (uV)
    lowpass_hz: float | None = None   # hardware-like zero-phase low-pass (-6 dB at this frequency)
    alpha_on_fraction: float = 1.0    # share of time alpha is on (bursty alpha if < 1)
    artefact_fraction: float = 0.0    # share of 2 s blocks with a large-amplitude burst
    flag_fraction: float = 0.0        # share of samples flagged INTERPOLATED by the "headset"


def aperiodic_psd(f: np.ndarray, t: Truth) -> np.ndarray:
    ff = np.maximum(f, 0.5)           # flat below 0.5 Hz so the variance is finite
    return 10 ** t.offset / ff ** t.exponent


def peak_gain(f: np.ndarray, peaks) -> np.ndarray:
    g = np.zeros_like(f)
    for cf, h, sd in peaks:
        g += h * np.exp(-(f - cf) ** 2 / (2 * sd ** 2))
    return 10 ** g


def _synth(psd: np.ndarray, n: int, sfreq: float, rng) -> np.ndarray:
    """Gaussian noise with the given one-sided PSD (uV^2/Hz) on the rfft grid."""
    amp = np.sqrt(psd * sfreq * n / 2)
    X = amp * (rng.standard_normal(len(psd)) + 1j * rng.standard_normal(len(psd))) / np.sqrt(2)
    X[0] = 0
    return np.fft.irfft(X, n)


def synthesise(t: Truth, n_sec: float, sfreq: float, rng, n_channels: int = 2, shared: float = 0.7):
    """channels x samples array in microvolts."""
    n = int(round(n_sec * sfreq))
    f = np.fft.rfftfreq(n, 1 / sfreq)
    ap = aperiodic_psd(f, t) * peak_gain(f, t.extra_peaks)
    alpha = aperiodic_psd(f, t) * (peak_gain(f, [(t.alpha_cf, t.alpha_height, t.alpha_sd)]) - 1) \
        if t.alpha_height > 0 else None

    def mix(psd):
        common = _synth(psd, n, sfreq, rng)
        return np.stack([np.sqrt(shared) * common + np.sqrt(1 - shared) * _synth(psd, n, sfreq, rng)
                         for _ in range(n_channels)])

    x = mix(ap)
    if alpha is not None:
        a = mix(alpha)
        if t.alpha_on_fraction < 1:   # alpha switched on and off in 2 s blocks, smooth edges
            block = int(2 * sfreq)
            on = (rng.random(n // block + 1) < t.alpha_on_fraction).astype(float)
            env = np.repeat(on, block)[:n]
            k = int(0.25 * sfreq)
            env = np.convolve(env, np.hanning(k) / np.hanning(k).sum(), mode="same")
            a = a * env
        x = x + a
    if t.floor_cross_hz:
        level = aperiodic_psd(np.array([t.floor_cross_hz]), t)[0]
        x = x + rng.standard_normal(x.shape) * np.sqrt(level * sfreq / 2)
    if t.lowpass_hz:
        from scipy.signal import butter, sosfiltfilt
        # sosfiltfilt doubles the order: 2nd order twice = 4th-order magnitude, -6 dB at the corner
        x = sosfiltfilt(butter(2, t.lowpass_hz / (sfreq / 2), output="sos"), x, axis=1)
    if t.line_uv:
        tt = np.arange(n) / sfreq
        x = x + t.line_uv * np.sin(2 * np.pi * 50.0 * tt + rng.uniform(0, 2 * np.pi))
    if t.artefact_fraction:
        block = int(2 * sfreq)
        for b in range(n // block):
            if rng.random() < t.artefact_fraction:
                x[:, b * block:(b + 1) * block] += 8 * x.std() * rng.standard_normal((n_channels, block))
    return x


def make_raw(x_uv: np.ndarray, sfreq: float, ch_names, flag: np.ndarray | None = None, eq: float = 4.0):
    """mne RawArray that looks like an Emotiv file: EEG channels (volts) + quality channels."""
    import mne
    mne.set_log_level("ERROR")
    n = x_uv.shape[1]
    aux_names = ["INTERPOLATED"] + [f"EQ_{c}" for c in ch_names] + [f"CQ_{c}" for c in ch_names]
    aux = [flag if flag is not None else np.zeros(n)]
    aux += [np.full(n, eq) for _ in ch_names] + [np.full(n, 4.0) for _ in ch_names]
    data = np.vstack([x_uv, np.array(aux)]) / 1e6
    info = mne.create_info(list(ch_names) + aux_names, sfreq, ["eeg"] * len(ch_names) + ["misc"] * len(aux_names))
    return mne.io.RawArray(data, info)


def pipeline_spectrum(x_uv, sfreq, ch_names=("O1", "O2"), flag=None, average=C.WELCH_AVERAGE, eq=4.0):
    """Simulated array -> same filter, epoching, rejection and Welch as the real pipeline.

    Returns (freqs, psd channels x freqs, qc dict with the same fields as preprocess.py).
    """
    import preprocess as P
    import psd as PSD
    raw = make_raw(x_uv, sfreq, ch_names, flag, eq)
    raw, aux = P.prepare(raw)
    starts, keep, info = P.accepted_epochs(raw, aux)
    info.update(n_epochs=int(len(starts)), n_epochs_kept=int(keep.sum()),
                share_epochs_kept=float(keep.mean()) if len(keep) else np.nan,
                clean_sec=float(P.clean_seconds(starts, keep, sfreq, raw.n_times)),
                accepted_starts=json.dumps(starts[keep].tolist()), sfreq=sfreq,
                duration_sec=raw.n_times / sfreq, n_eeg_channels=len(raw.ch_names))
    if keep.sum() == 0:
        return None, None, info
    f, p = PSD.epoch_spectra(raw.get_data() * P.UV, starts[keep].tolist(), sfreq, average)
    return f, p, info


def simulate_and_fit(t: Truth, clean_sec: float = 180.0, rng=None, sfreq: float = SFREQ,
                     average: str = C.WELCH_AVERAGE, fit_range=C.FIT_RANGE, mode=C.APERIODIC_MODE,
                     min_height=C.MIN_PEAK_HEIGHT) -> dict:
    """One simulated recording through the whole chain. Returns estimates next to the truth."""
    import fit_specparam as F
    import psd as PSD
    rng = rng or np.random.default_rng()
    x = synthesise(t, clean_sec, sfreq, rng)
    flag = (rng.random(x.shape[1]) < t.flag_fraction).astype(float) if t.flag_fraction else None
    f, p, info = pipeline_spectrum(x, sfreq, flag=flag, average=average)
    out = {f"true_{k}": v for k, v in asdict(t).items() if k != "extra_peaks"}
    out.update(rec_sec=clean_sec, sfreq=sfreq, average=average, kept_sec=info["clean_sec"],
               share_epochs_kept=info["share_epochs_kept"],
               line_noise_ratio=PSD.line_noise_from_array(x, sfreq))
    if f is None:
        out.update(F.features(None))
        return out
    spec = p.mean(axis=0)
    out.update(F.features(F.fit_one(f, spec, fit_range, mode, min_height)))
    out["sg_present"], out["sg_iaf"] = F.sg_detect(f, spec)
    out["raw_peak_7_12"] = F.raw_peak(f, spec)
    return out


# ------------------------------------------------------------------ experiments
def _draw(rng, **fixed) -> Truth:
    """Random nuisance values (alpha frequency, width, offset) around fixed settings."""
    base = dict(alpha_cf=rng.uniform(8, 12), alpha_sd=rng.uniform(0.6, 1.5), offset=rng.uniform(0.5, 1.5))
    base.update(fixed)
    return Truth(**base)


def exp_A(n, rng):
    """Main grid: exponent x alpha height x recording length."""
    for ex, h, sec in itertools.product([0.5, 1.0, 1.5, 2.0], [0, .05, .1, .15, .2, .3, .5, .8],
                                        [30, 60, 120, 180]):
        for _ in range(n):
            yield dict(cell=f"exp{ex}_h{h}_sec{sec}"), _draw(rng, exponent=ex, alpha_height=h), dict(clean_sec=sec)


def exp_B(n, rng):
    """50 Hz line noise of increasing amplitude."""
    for uv, h in itertools.product([0, 2, 10, 50, 200], [0, 0.2]):
        for _ in range(n):
            yield dict(cell=f"line{uv}_h{h}"), _draw(rng, exponent=1.2, alpha_height=h, line_uv=uv), dict(clean_sec=120)


def exp_C(n, rng):
    """White sensor-noise floor that flattens the spectrum above a crossing frequency."""
    for fc, h in itertools.product([None, 40, 25, 15, 8], [0, 0.2, 0.4]):
        for _ in range(n):
            yield (dict(cell=f"floor{fc}_h{h}"), _draw(rng, exponent=1.5, alpha_height=h, floor_cross_hz=fc),
                   dict(clean_sec=120))


def exp_D(n, rng):
    """Hardware-like low-pass near the top of the fit range (the true headset filter is not documented here)."""
    for lp, h in itertools.product([None, 43, 35], [0, 0.2, 0.4]):
        for _ in range(n):
            yield (dict(cell=f"lowpass{lp}_h{h}"), _draw(rng, exponent=1.2, alpha_height=h, lowpass_hz=lp),
                   dict(clean_sec=120))


def exp_E(n, rng):
    """Alpha peaks near the edges of the 7-14 Hz window."""
    for cf in [6.5, 7.0, 7.25, 7.5, 8.0, 13.0, 13.5, 13.75, 14.0, 14.5]:
        for _ in range(n):
            yield dict(cell=f"cf{cf}"), _draw(rng, exponent=1.2, alpha_height=0.4, alpha_cf=cf, alpha_sd=1.0), \
                dict(clean_sec=120)


def exp_F(n, rng):
    """Intermittent alpha: median Welch (pre-registered) vs mean Welch."""
    for on, h, avg in itertools.product([1.0, 0.75, 0.5, 0.35, 0.2], [0.3, 0.6], ["median", "mean"]):
        for _ in range(n):
            yield (dict(cell=f"on{on}_h{h}_{avg}"), _draw(rng, exponent=1.2, alpha_height=h, alpha_on_fraction=on),
                   dict(clean_sec=180, average=avg))


def exp_G(n, rng):
    """Other peaks without alpha: theta (6 Hz), low beta (15, 20 Hz); and a very broad alpha."""
    cases = {"theta6_noalpha": dict(alpha_height=0, extra_peaks=((6.0, 0.4, 1.0),)),
             "theta6.5_noalpha": dict(alpha_height=0, extra_peaks=((6.5, 0.4, 1.0),)),
             "beta15_noalpha": dict(alpha_height=0, extra_peaks=((15.0, 0.4, 1.5),)),
             "beta20_noalpha": dict(alpha_height=0, extra_peaks=((20.0, 0.4, 2.0),)),
             "alpha_plus_beta20": dict(alpha_height=0.4, extra_peaks=((20.0, 0.3, 2.0),)),
             "broad_alpha_sd3": dict(alpha_height=0.3, alpha_sd=3.0),
             "narrow_alpha_sd0.3": dict(alpha_height=0.3, alpha_sd=0.3)}
    for name, kw in cases.items():
        for _ in range(n):
            yield dict(cell=name), _draw(rng, exponent=1.2, **kw), dict(clean_sec=120)


def exp_H(n, rng):
    """128 Hz vs 256 Hz sampling (7 Indian participants were recorded at 256 Hz)."""
    for sf, h in itertools.product([128.0, 256.0], [0, 0.2, 0.4]):
        for _ in range(n):
            yield dict(cell=f"sf{int(sf)}_h{h}"), _draw(rng, exponent=1.2, alpha_height=h), dict(clean_sec=120, sfreq=sf)


def exp_I(n, rng):
    """Artefact bursts and headset 'interpolated' flags: does epoch rejection protect the estimates?"""
    for art, flag, h in itertools.product([0, 0.1, 0.3], [0, 0.0005], [0, 0.3]):
        for _ in range(n):
            yield (dict(cell=f"art{art}_flag{flag}_h{h}"),
                   _draw(rng, exponent=1.2, alpha_height=h, artefact_fraction=art, flag_fraction=flag),
                   dict(clean_sec=180))


def exp_J(n, rng):
    """Fit settings from the robustness grid, on clean simulated data."""
    for fr, mode, h in itertools.product([(2.0, 40.0), (1.0, 40.0), (3.0, 30.0)], ["fixed", "knee"], [0, 0.2]):
        for _ in range(n):
            yield (dict(cell=f"range{fr[0]:g}-{fr[1]:g}_{mode}_h{h}"), _draw(rng, exponent=1.2, alpha_height=h),
                   dict(clean_sec=120, fit_range=fr, mode=mode))


EXPERIMENTS = {"A": exp_A, "B": exp_B, "C": exp_C, "D": exp_D, "E": exp_E,
               "F": exp_F, "G": exp_G, "H": exp_H, "I": exp_I, "J": exp_J}


def run_experiments(out: Path, n: int, only: list[str] | None = None, seed: int = 20261125) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for i, (name, gen) in enumerate(EXPERIMENTS.items()):
        if only and name not in only:
            continue
        path = out / f"exp_{name}.csv"
        if path.exists():
            print(f"{name}: exists, skipped")
            continue
        rng = np.random.default_rng(seed + i)
        t0, rows = time.time(), []
        n_here = n if name == "A" else 2 * n   # smaller experiments get twice the repetitions
        for tags, truth, kw in gen(n_here, rng):
            rows.append({**tags, **simulate_and_fit(truth, rng=rng, **kw)})
        pd.DataFrame(rows).to_csv(path, index=False)
        print(f"{name}: {len(rows)} simulations in {time.time() - t0:.0f} s", flush=True)


def run_threshold_calibration(out: Path, n: int = 200, seed: int = 20261126) -> None:
    """Experiment K: how the presence rule behaves under different thresholds.

    Each simulated recording is fitted with every minimum peak height of the
    robustness grid (plus 0.4), with a stricter peak threshold (3 SD), and from a
    mean-Welch spectrum. For every fit we keep whether a 7-14 Hz peak was returned
    and the height and width of the tallest one, so that any rule of the form
    "fitted height >= T" can be evaluated afterwards. Output: exp_K.csv (long format).
    """
    import fit_specparam as F
    path = out / "exp_K.csv"
    if path.exists():
        print("K: exists, skipped")
        return
    rng = np.random.default_rng(seed)
    variants = [("median", mh, 2.0) for mh in (0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4)] + \
               [("median", 0.1, 3.0), ("mean", 0.1, 2.0), ("mean", 0.3, 2.0)]
    rows, t0 = [], time.time()
    for h, sec in itertools.product([0, 0.1, 0.2, 0.3, 0.4, 0.6], [60, 120, 180]):
        for i in range(n):
            t = _draw(rng, exponent=rng.uniform(0.5, 2.0), alpha_height=h)
            x = synthesise(t, sec, SFREQ, rng)
            spectra = {avg: pipeline_spectrum(x, SFREQ, average=avg) for avg in ("median", "mean")}
            for avg, mh, thr in variants:
                f, p, info = spectra[avg]
                old_thr, C.PEAK_THRESHOLD = C.PEAK_THRESHOLD, thr
                try:
                    ft = F.features(F.fit_one(f, p.mean(axis=0), min_height=mh))
                finally:
                    C.PEAK_THRESHOLD = old_thr
                rows.append(dict(sim=f"{h}_{sec}_{i}", true_alpha_height=h, rec_sec=sec, true_exponent=t.exponent,
                                 true_alpha_cf=t.alpha_cf, average=avg, min_peak_height=mh, peak_threshold=thr,
                                 alpha_present=ft["alpha_present"], alpha_pw=ft.get("alpha_pw"),
                                 alpha_bw=ft.get("alpha_bw"), iaf=ft.get("iaf"), r2=ft.get("r2"),
                                 fit_error=ft.get("fit_error"), exponent=ft.get("exponent")))
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f"K: {len(rows)} fits in {time.time() - t0:.0f} s", flush=True)


def summarise(out: Path) -> pd.DataFrame:
    """One row per experiment cell: detection rates and recovery errors."""
    frames = []
    for path in sorted(out.glob("exp_[A-J].csv")):
        d = pd.read_csv(path)
        d["exp"] = path.stem[-1]
        d["alpha_present"] = d["alpha_present"].astype(str).str.lower().eq("true")
        d["sg_present"] = d["sg_present"].astype(str).str.lower().eq("true")
        d["iaf_err"] = d["iaf"] - d["true_alpha_cf"]
        d["exp_err"] = d["exponent"] - d["true_exponent"]
        d["pw_err"] = d["alpha_pw"] - d["true_alpha_height"]
        d["r2_below_floor"] = d["r2"] < C.R2_FLOOR
        g = d.groupby(["exp", "cell"], sort=False)
        frames.append(pd.DataFrame({
            "n": g.size(), "true_height": g["true_alpha_height"].first(),
            "specparam_present": g["alpha_present"].mean(), "sg_present": g["sg_present"].mean(),
            "iaf_bias": g["iaf_err"].mean(), "iaf_mae": g["iaf_err"].apply(lambda v: v.abs().mean()),
            "iaf_err_gt1hz": g["iaf_err"].apply(lambda v: (v.abs() > 1).sum() / max(v.notna().sum(), 1)),
            "raw_peak_mae": g.apply(lambda v: (v["raw_peak_7_12"] - v["true_alpha_cf"]).abs().mean()),
            "exponent_bias": g["exp_err"].mean(), "exponent_sd": g["exp_err"].std(),
            "alpha_pw_bias": g["pw_err"].mean(), "r2_median": g["r2"].median(),
            "r2_below_floor": g["r2_below_floor"].mean(), "kept_sec": g["kept_sec"].median(),
            "line_noise_ratio": g["line_noise_ratio"].median(),
        }).reset_index())
    s = pd.concat(frames, ignore_index=True)
    s.to_csv(out / "summary.csv", index=False)
    return s


# ------------------------------------------------------------------ simulated cohort
PLANTED = {"iaf_slope": -0.12, "exponent_slope": -0.06, "alpha_height_slope": 0.0,
           "income_effect": 0.0, "true_no_alpha_share": 0.08}
AGE_P = {"18-20": .15, "21-24": .12, "25-34": .22, "35-44": .20, "45-54": .15, "55-64": .10, "65-74": .05, "75-84": .01}


def make_cohort(n_per_site: int, seed: int = 7) -> None:
    """Write a simulated study into C.BASE (requires ALPHA_SIM_ROOT). Planted effects: PLANTED."""
    assert C.SIMULATION, "make_cohort only runs with ALPHA_SIM_ROOT set"
    import psd as PSD
    rng = np.random.default_rng(seed)
    (C.DERIV / "psd").mkdir(parents=True, exist_ok=True)
    (C.DERIV / "qc").mkdir(parents=True, exist_ok=True)
    C.RESULTS.mkdir(parents=True, exist_ok=True)
    (C.BASE / "SIMULATED_DATA").write_text("Everything in this folder is simulated.\n")
    clusters = {"India": ["ANAN", "PORA", "VIDH", "SUAR", "KAGU", "ARPA"],
                "Tanzania": ["JOLA", "ADMU", "RARW", "LABE", "JOMO", "UPSA", "KESH", "WIJU", "NEGA", "ISMW"]}
    meta, qc, ln, truth = [], [], [], []
    for site in ("India", "Tanzania"):
        cl_shift = {c: rng.normal(0, 0.05) for c in clusters[site]}
        for i in range(n_per_site):
            cl = clusters[site][rng.integers(len(clusters[site]))]
            pid = f"sub-{cl}{i:04d}"
            ag = rng.choice(list(AGE_P), p=np.array(list(AGE_P.values())) / sum(AGE_P.values()))
            age = C.AGE_MIDPOINTS[ag]
            dec = (age - 38) / 10
            q = rng.normal()                                  # latent recording quality
            income_ord = float(rng.integers(0, 6)) if site == "India" else np.nan
            has_alpha = rng.random() > PLANTED["true_no_alpha_share"]
            t_ec = Truth(exponent=float(np.clip(1.3 + PLANTED["exponent_slope"] * dec + cl_shift[cl]
                                                + rng.normal(0, 0.25), 0.3, 2.5)),
                         offset=rng.normal(1.0, 0.3),
                         alpha_height=float(np.clip(rng.normal(0.55, 0.22), 0.05, None)) if has_alpha else 0.0,
                         alpha_cf=float(np.clip(10.0 + PLANTED["iaf_slope"] * dec + rng.normal(0, 0.9), 7.5, 13)),
                         alpha_sd=rng.uniform(0.6, 1.5),
                         floor_cross_hz=float(np.clip(10 ** (1.7 + 0.2 * q), 6, 120)),
                         line_uv=float(abs(rng.normal(0, 3))), flag_fraction=0.0002)
            montage = "In1" if site == "India" else rng.choice(["Ta1", "Ta2", "other"], p=[.6, .17, .23])
            chans = ["O1", "O2", "P7", "P8", "AF3"] if montage != "other" else ["O1", "O2", "AF3"]
            sf = 256.0 if (site == "India" and i < 4) else SFREQ
            for task in ("ec", "eo"):
                t = Truth(**{**asdict(t_ec), "alpha_height": t_ec.alpha_height * (1.0 if task == "ec" else 0.35)})
                sec = float(rng.uniform(150, 200))
                x = synthesise(t, sec, sf, rng, n_channels=len(chans))
                flag = (rng.random(x.shape[1]) < t.flag_fraction).astype(float)
                eq = float(np.clip(3.4 + 0.4 * q + rng.normal(0, 0.2), 0, 4))
                f, p, info = pipeline_spectrum(x, sf, ch_names=chans, flag=flag, eq=eq)
                usable = info["clean_sec"] >= C.MIN_CLEAN_SEC
                if usable:
                    PSD.save_psd(C.DERIV / "psd" / f"{pid}_{task}.npz", f, p, chans)
                    ln.append(dict(participant_id=pid, task=task,
                                   line_noise_ratio=PSD.line_noise_from_array(x[:2], sf)))
                qc.append(dict(participant_id=pid, task=task, **info, EQ_O1=eq, CQ_O1=4.0, EQ_O2=eq, CQ_O2=4.0,
                               EQ_roi=eq, CQ_roi=4.0 if q > -1.5 else 3.0, blink_channel="AF3",
                               blinks_per_min=0.0, usable=bool(usable), status="ok"))
            meta.append(dict(participant_id=pid, site=site, age_group=ag, age_years=age, adult=True,
                             sex=rng.choice(["F", "M"]), income_usd="sim", income_ord=income_ord,
                             income_rank_z=np.nan, mhq_score=np.nan, researcher=cl, researcher_cluster=cl,
                             montage_family=montage, has_O1O2=True, has_posterior4=montage != "other",
                             analysable=True))
            truth.append(dict(participant_id=pid, site=site, quality_latent=q, **asdict(t_ec)))
    meta = pd.DataFrame(meta)
    ok = meta["income_ord"].notna()
    r = meta.loc[ok, "income_ord"].rank(pct=True)
    meta.loc[ok, "income_rank_z"] = (r - r.mean()) / r.std()
    meta.to_csv(C.RESULTS / "participants_clean.csv", index=False)
    qc = pd.DataFrame(qc)
    qc.to_csv(C.DERIV / "qc" / "qc_all.csv", index=False)
    qc.drop(columns=["accepted_starts"]).to_csv(C.RESULTS / "qc_summary.csv", index=False)
    pd.DataFrame(ln).to_csv(C.RESULTS / "line_noise.csv", index=False)
    pd.DataFrame(truth).drop(columns=["extra_peaks"]).to_csv(C.RESULTS / "truth.csv", index=False)


def run_pipeline(grid: bool = True, jobs: int = 1, n_null: int = 100) -> pd.DataFrame:
    """fit_specparam -> models -> robustness -> figures on the simulated cohort, then compare with the truth."""
    assert C.SIMULATION, "run_pipeline only runs with ALPHA_SIM_ROOT set"
    import figures
    import fit_specparam as F
    import models as M
    import robustness as R
    t0 = time.time()
    feats, _ = F.run(jobs=jobs, grid=grid)
    print(f"fits: {time.time() - t0:.0f} s", flush=True)
    res = M.run()
    if grid:
        R.run(n_null=n_null)
        figures.run()
    truth = pd.read_csv(C.RESULTS / "truth.csv")
    df = M.load().merge(truth, on=["participant_id", "site"], suffixes=("", "_true"))
    rows = []
    for site, g in df.groupby("site"):
        gp = g[g["alpha_present"] & (g["alpha_height"] > 0)]
        get = lambda t: res[(res["site"] == site) & (res["test"] == t)].iloc[0]  # noqa: E731
        rows += [
            dict(site=site, quantity="share with planted alpha", truth=(g["alpha_height"] > 0).mean(),
                 estimate=g["alpha_present"].mean()),
            dict(site=site, quantity="false 'absent' among planted alpha", truth=0.0,
                 estimate=(~g.loc[g["alpha_height"] > 0, "alpha_present"]).mean()),
            dict(site=site, quantity="false 'present' among no planted alpha", truth=0.0,
                 estimate=g.loc[g["alpha_height"] == 0, "alpha_present"].mean()),
            dict(site=site, quantity="IAF mean abs error (Hz)", truth=0.0,
                 estimate=(gp["iaf"] - gp["alpha_cf"]).abs().mean()),
            dict(site=site, quantity="H3 IAF slope per decade", truth=PLANTED["iaf_slope"],
                 estimate=get("H3 IAF ~ age")["estimate"], ci_low=get("H3 IAF ~ age")["ci_low"],
                 ci_high=get("H3 IAF ~ age")["ci_high"]),
            dict(site=site, quantity="H4 exponent slope per decade", truth=PLANTED["exponent_slope"],
                 estimate=get("H4 exponent ~ age")["estimate"], ci_low=get("H4 exponent ~ age")["ci_low"],
                 ci_high=get("H4 exponent ~ age")["ci_high"]),
            dict(site=site, quantity="H5 alpha power slope (SD per decade)", truth=0.0,
                 estimate=get("H5 alpha power equivalence")["estimate"],
                 ci_low=get("H5 alpha power equivalence")["ci_low"],
                 ci_high=get("H5 alpha power equivalence")["ci_high"]),
        ]
    rec = pd.DataFrame(rows)
    rec.to_csv(C.RESULTS / "recovery.csv", index=False)
    return rec


def _reexec_in_sim_root(root: Path) -> None:
    """Restart this script with ALPHA_SIM_ROOT set, so config.py points every path at the simulation folder."""
    if os.environ.get("ALPHA_SIM_ROOT") != str(root):
        env = {**os.environ, "ALPHA_SIM_ROOT": str(root)}
        sys.exit(subprocess.run([sys.executable, *sys.argv], env=env).returncode)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("experiments")
    e.add_argument("--out", type=Path, required=True)
    e.add_argument("--n", type=int, default=200)
    e.add_argument("--only", type=str, default="")
    e.add_argument("--n-calibration", type=int, default=200)
    c = sub.add_parser("cohort")
    c.add_argument("--root", type=Path, required=True)
    c.add_argument("--n-per-site", type=int, default=300)
    c.add_argument("--no-grid", action="store_true")
    c.add_argument("--jobs", type=int, default=1)
    args = ap.parse_args()
    if args.cmd == "experiments":
        only = [s for s in args.only.split(",") if s] or None
        run_experiments(args.out, args.n, only)
        if not only or "K" in only:
            run_threshold_calibration(args.out, args.n_calibration)
        print(summarise(args.out).round(3).to_string())
    else:
        root = args.root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        _reexec_in_sim_root(root)
        if not (C.RESULTS / "truth.csv").exists():
            make_cohort(args.n_per_site)
        print(run_pipeline(grid=not args.no_grid, jobs=args.jobs).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
