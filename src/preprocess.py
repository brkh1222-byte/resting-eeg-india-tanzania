"""Preprocessing: load, filter, epoch, reject artefacts, and record quality.

How it works (plain-language version for the methods section):
 1. Read the EDF with MNE and keep only EEG electrodes.
 2. Band-pass filter 1-45 Hz (removes slow drift and anything near the
    64 Hz Nyquist limit of 128 Hz data).
 3. Cut 4 s epochs that overlap by 50% (a new epoch every 2 s).
 4. Reject an epoch if (a) the Emotiv headset flagged interpolated or
    saturated samples in it, or (b) its variance on O1 or O2 is an outlier
    for that person (robust z-score > 3 on log-variance). A relative rule is
    used because a consumer headset's absolute voltages are not calibrated.
 5. A recording is usable if O1 and O2 exist, are not flat, and at least
    60 s of clean data remain.
 6. Record quality metrics: Emotiv signal-quality (EQ) and contact-quality
    (CQ) at O1/O2, share of epochs kept, interpolated-sample share, and the
    frontal blink rate (blinks should be near zero with eyes closed).

This step computes NO spectra. It saves a QC table and the list of
accepted epochs; src/psd.py re-creates the clean epochs from that list.

Run:  .venv/bin/python src/preprocess.py [--limit N] [--jobs 6]
Output: data/derivatives/qc/qc_<task>.csv (git-ignored) and
        results/qc_summary.csv (one row per recording, committed)
"""
import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt, find_peaks

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402

UV = 1e6  # MNE stores volts; Emotiv EDF values are microvolts


def edf_path(pid: str, task: str) -> Path:
    return C.DATA / pid / "eeg" / f"{pid}_task-{task}_eeg.edf"


def load_filtered(pid: str, task: str):
    """Return (mne.io.Raw with EEG only, filtered; dict of raw auxiliary channels)."""
    import mne
    mne.set_log_level("ERROR")
    raw = mne.io.read_raw_edf(edf_path(pid, task), preload=True)
    names = raw.ch_names
    eeg = [n for n in names if n not in C.NON_EEG_NAMES and not n.startswith(C.NON_EEG_PREFIXES)]
    aux_names = [n for n in names if n.startswith(("EQ_", "CQ_")) or n in ("INTERPOLATED", "SaturationFlag")]
    aux = {n: raw.get_data(picks=[n])[0] * UV for n in aux_names}
    raw.pick(eeg)
    raw.set_channel_types({n: "eeg" for n in eeg})
    raw.filter(C.L_FREQ, C.H_FREQ, fir_design="firwin")
    return raw, aux


def epoch_starts(n_times: int, sfreq: float) -> np.ndarray:
    win = int(C.EPOCH_SEC * sfreq)
    step = int(win * (1 - C.EPOCH_OVERLAP))
    return np.arange(0, n_times - win + 1, step)


def robust_z(x: np.ndarray) -> np.ndarray:
    med = np.median(x)
    mad = np.median(np.abs(x - med)) * 1.4826
    return (x - med) / mad if mad > 0 else np.zeros_like(x)


def blink_rate(sig_uv: np.ndarray, sfreq: float) -> float:
    """Blinks per minute on a frontal channel: peaks > 75 uV in a 1-8 Hz band, >= 0.3 s apart."""
    b, a = butter(2, [1 / (sfreq / 2), 8 / (sfreq / 2)], btype="band")
    x = filtfilt(b, a, sig_uv)
    peaks, _ = find_peaks(np.abs(x), height=75, distance=int(0.3 * sfreq))
    return len(peaks) / (len(x) / sfreq / 60)


def accepted_epochs(raw, aux) -> tuple[np.ndarray, np.ndarray, dict]:
    """Return (starts of all epochs, boolean mask of accepted epochs, info dict)."""
    sfreq = raw.info["sfreq"]
    win = int(C.EPOCH_SEC * sfreq)
    starts = epoch_starts(raw.n_times, sfreq)
    keep = np.ones(len(starts), bool)
    info = {}

    flag = np.zeros(raw.n_times, bool)
    for n in ("INTERPOLATED", "SaturationFlag"):
        if n in aux:
            flag |= aux[n] != 0
    info["interpolated_share"] = float(flag.mean())
    keep &= np.array([not flag[s:s + win].any() for s in starts], dtype=bool)

    roi = [c for c in C.ROI_PRIMARY if c in raw.ch_names]
    info["roi_sd_uv"] = np.nan
    if roi:  # some recordings (mostly Tanzanian eyes-open) lack O1/O2
        data = raw.get_data(picks=roi) * UV
        info["roi_sd_uv"] = float(np.median(data.std(axis=1)))
        logvar = np.array([[np.log(data[i, s:s + win].var()) for s in starts] for i in range(len(roi))])
        keep &= ~(np.array([robust_z(lv) > C.REJECT_ROBUST_Z for lv in logvar]).any(axis=0))
    return starts, keep, info


def clean_seconds(starts: np.ndarray, keep: np.ndarray, sfreq: float, n_times: int) -> float:
    covered = np.zeros(n_times, bool)
    win = int(C.EPOCH_SEC * sfreq)
    for s in starts[keep]:
        covered[s:s + win] = True
    return covered.sum() / sfreq


def process_one(args: tuple[str, str]) -> dict:
    """Wrapper: one bad recording is logged as a status, never crashes the whole run."""
    try:
        return _process_one(args)
    except Exception as exc:
        return {"participant_id": args[0], "task": args[1], "status": f"error: {exc}", "usable": False}


def _process_one(args: tuple[str, str]) -> dict:
    pid, task = args
    row = {"participant_id": pid, "task": task}
    if not edf_path(pid, task).exists():
        row["status"] = "missing_file"
        return row
    try:
        raw, aux = load_filtered(pid, task)
    except Exception as exc:
        row["status"] = f"read_error: {exc}"
        return row
    sfreq = raw.info["sfreq"]
    row["sfreq"] = sfreq
    row["duration_sec"] = raw.n_times / sfreq
    row["n_eeg_channels"] = len(raw.ch_names)

    starts, keep, info = accepted_epochs(raw, aux)
    row.update(info)
    row["n_epochs"] = int(len(starts))
    row["n_epochs_kept"] = int(keep.sum())
    row["share_epochs_kept"] = float(keep.mean()) if len(keep) else np.nan
    row["clean_sec"] = clean_seconds(starts, keep, sfreq, raw.n_times)

    for ch in C.ROI_PRIMARY:
        row[f"EQ_{ch}"] = float(np.mean(aux[f"EQ_{ch}"])) if f"EQ_{ch}" in aux else np.nan
        row[f"CQ_{ch}"] = float(np.mean(aux[f"CQ_{ch}"])) if f"CQ_{ch}" in aux else np.nan
    row["EQ_roi"] = np.nanmean([row["EQ_O1"], row["EQ_O2"]])
    row["CQ_roi"] = np.nanmean([row["CQ_O1"], row["CQ_O2"]])

    front = [c for c in C.FRONTAL_BLINK_CHANNELS if c in raw.ch_names]
    row["blink_channel"] = front[0] if front else ""
    row["blinks_per_min"] = blink_rate(raw.get_data(picks=[front[0]])[0] * UV, sfreq) if front else np.nan

    has_roi = all(c in raw.ch_names for c in C.ROI_PRIMARY)
    flat = has_roi and (raw.get_data(picks=C.ROI_PRIMARY) * UV).std(axis=1).min() < 1.0
    row["usable"] = bool(has_roi and not flat and row["clean_sec"] >= C.MIN_CLEAN_SEC)
    row["status"] = "ok"
    row["accepted_starts"] = json.dumps(starts[keep].tolist())
    return row


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()

    meta = pd.read_csv(C.RESULTS / "participants_clean.csv")
    pids = meta.loc[meta["analysable"], "participant_id"].tolist()
    if args.limit:
        pids = pids[: args.limit]
    out_dir = C.DERIV / "qc"
    out_dir.mkdir(parents=True, exist_ok=True)

    jobs = [(p, t) for p in pids for t in C.TASKS]
    with ProcessPoolExecutor(args.jobs) as pool:
        rows = list(pool.map(process_one, jobs, chunksize=4))
    qc = pd.DataFrame(rows)
    qc.to_csv(out_dir / "qc_all.csv", index=False)               # includes epoch lists
    qc.drop(columns=["accepted_starts"], errors="ignore").to_csv(C.RESULTS / "qc_summary.csv", index=False)
    print(qc.groupby("task")[["usable"]].mean())
    print(qc["status"].value_counts().head())


if __name__ == "__main__":
    main()
