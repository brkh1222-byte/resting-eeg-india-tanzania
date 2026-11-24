"""Power spectra for every usable recording (eyes closed and eyes open).

Method: each accepted 4 s epoch (from src/preprocess.py) gets a Hann-windowed
periodogram (0.25 Hz resolution); the spectrum is the MEDIAN across epochs,
i.e. Welch's method with a median average, which resists leftover artefacts.
The median is NOT bias-corrected (the median of a periodogram is about
ln 2 = 0.69 of its mean), so the aperiodic offset is about 0.16 log10 lower
than a mean-Welch offset; the exponent and peak heights are unaffected.
A 50 Hz line-noise ratio (power 48-52 Hz / 40-45 Hz, unfiltered O1/O2) is also
saved as a data-quality metric.

Blocked until the pre-registration is committed (src/prereg_guard.py).

Run:  .venv/bin/python src/psd.py [--jobs 2]
Output: data/derivatives/psd/<pid>_<task>.npz (git-ignored),
        results/line_noise.csv, results/psd_failures.csv
Re-runnable: recordings whose .npz already exists are not recomputed.
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import welch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402
from prereg_guard import require_prereg  # noqa: E402
from preprocess import UV, edf_path, load_filtered  # noqa: E402


def epoch_spectra(data_uv: np.ndarray, starts: list[int], sfreq: float, average: str = C.WELCH_AVERAGE):
    """Spectrum per channel from the accepted epochs. data: channels x samples (uV).

    average="median" is the pre-registered estimator; "mean" exists only so the
    simulation study can show how the two differ when alpha is intermittent.
    """
    win = int(C.EPOCH_SEC * sfreq)
    per_epoch = []
    for s in starts:
        f, p = welch(data_uv[:, s:s + win], fs=sfreq, window="hann", nperseg=win,
                     noverlap=0, detrend="constant")
        per_epoch.append(p)
    stack = np.stack(per_epoch)
    return f, (np.median(stack, axis=0) if average == "median" else stack.mean(axis=0))


def line_noise_from_array(x_uv: np.ndarray, sfreq: float) -> float:
    """Power at 48-52 Hz divided by power at 40-45 Hz. x: channels x samples, unfiltered."""
    f, p = welch(x_uv, fs=sfreq, nperseg=int(4 * sfreq))
    p = p.mean(axis=0)
    return float(p[(f >= 48) & (f <= 52)].mean() / p[(f >= 40) & (f <= 45)].mean())


def line_noise_ratio(pid: str, task: str) -> float:
    import mne
    mne.set_log_level("ERROR")
    raw = mne.io.read_raw_edf(edf_path(pid, task), preload=True)
    return line_noise_from_array(raw.get_data(picks=C.ROI_PRIMARY) * UV, raw.info["sfreq"])


def save_psd(out: Path, freqs, psd, ch_names) -> None:
    np.savez_compressed(out, freqs=freqs, psd=psd.astype(np.float32), ch_names=np.array(ch_names))


def process_one(row: dict) -> dict:
    """One recording. A failure is returned as a status and never stops the run."""
    pid, task = row["participant_id"], row["task"]
    res = {"participant_id": pid, "task": task, "status": "ok", "line_noise_ratio": np.nan}
    out = C.DERIV / "psd" / f"{pid}_{task}.npz"
    try:
        if not out.exists():
            raw, _ = load_filtered(pid, task)
            starts = json.loads(row["accepted_starts"])
            f, psd = epoch_spectra(raw.get_data() * UV, starts, raw.info["sfreq"])
            save_psd(out, f, psd, raw.ch_names)
        res["line_noise_ratio"] = line_noise_ratio(pid, task)
    except Exception as exc:  # logged in results/psd_failures.csv
        res["status"] = f"error: {exc}"
    return res


def run(jobs: int = 2) -> pd.DataFrame:
    qc = pd.read_csv(C.DERIV / "qc" / "qc_all.csv")
    rows = qc[qc["usable"] == True].to_dict("records")  # noqa: E712
    (C.DERIV / "psd").mkdir(parents=True, exist_ok=True)
    if jobs == 1:
        out = [process_one(r) for r in rows]
    else:
        with ProcessPoolExecutor(jobs) as pool:
            out = list(pool.map(process_one, rows, chunksize=4))
    out = pd.DataFrame(out)
    out[out["status"] == "ok"].drop(columns="status").to_csv(C.RESULTS / "line_noise.csv", index=False)
    out[out["status"] != "ok"].to_csv(C.RESULTS / "psd_failures.csv", index=False)
    return out


def main() -> None:
    commit = require_prereg()
    print("Pre-registration commit:", commit)
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=2)
    args = ap.parse_args()
    out = run(args.jobs)
    print(f"{(out['status'] == 'ok').sum()} spectra written, {(out['status'] != 'ok').sum()} failed")


if __name__ == "__main__":
    main()
