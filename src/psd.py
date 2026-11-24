"""Power spectra for every usable recording (eyes closed and eyes open).

Method: each accepted 4 s epoch (from src/preprocess.py) gets a Hann-windowed
periodogram (0.25 Hz resolution); the spectrum is the MEDIAN across epochs,
i.e. Welch's method with a median average, which resists leftover artefacts.
A 50 Hz line-noise ratio (power 48-52 Hz / 40-45 Hz, unfiltered O1/O2) is also
saved as a data-quality metric.

Blocked until the pre-registration is committed (src/prereg_guard.py).

Run:  .venv/bin/python src/psd.py [--jobs 6]
Output: data/derivatives/psd/<pid>_<task>.npz (git-ignored),
        results/line_noise.csv
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


def epoch_spectra(data_uv: np.ndarray, starts: list[int], sfreq: float):
    """Median-across-epochs spectrum per channel. data: channels x samples (uV)."""
    win = int(C.EPOCH_SEC * sfreq)
    per_epoch = []
    for s in starts:
        f, p = welch(data_uv[:, s:s + win], fs=sfreq, window="hann", nperseg=win,
                     noverlap=0, detrend="constant")
        per_epoch.append(p)
    return f, np.median(np.stack(per_epoch), axis=0)


def line_noise_ratio(pid: str, task: str) -> float:
    import mne
    mne.set_log_level("ERROR")
    raw = mne.io.read_raw_edf(edf_path(pid, task), preload=True)
    x = raw.get_data(picks=C.ROI_PRIMARY) * UV
    f, p = welch(x, fs=raw.info["sfreq"], nperseg=int(4 * raw.info["sfreq"]))
    p = p.mean(axis=0)
    return float(p[(f >= 48) & (f <= 52)].mean() / p[(f >= 40) & (f <= 45)].mean())


def process_one(row: dict) -> dict:
    pid, task = row["participant_id"], row["task"]
    raw, _ = load_filtered(pid, task)
    starts = json.loads(row["accepted_starts"])
    f, psd = epoch_spectra(raw.get_data() * UV, starts, raw.info["sfreq"])
    out = C.DERIV / "psd" / f"{pid}_{task}.npz"
    np.savez_compressed(out, freqs=f, psd=psd.astype(np.float32), ch_names=np.array(raw.ch_names))
    return {"participant_id": pid, "task": task, "line_noise_ratio": line_noise_ratio(pid, task)}


def main() -> None:
    commit = require_prereg()
    print("Pre-registration commit:", commit)
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()
    qc = pd.read_csv(C.DERIV / "qc" / "qc_all.csv")
    rows = qc[qc["usable"] == True].to_dict("records")  # noqa: E712
    (C.DERIV / "psd").mkdir(parents=True, exist_ok=True)
    with ProcessPoolExecutor(args.jobs) as pool:
        out = list(pool.map(process_one, rows, chunksize=4))
    pd.DataFrame(out).to_csv(C.RESULTS / "line_noise.csv", index=False)
    print(f"{len(out)} spectra written")


if __name__ == "__main__":
    main()
