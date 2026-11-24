"""Download the parts of OpenNeuro ds007358 v1.0.0 this project uses.

What it fetches (public S3, no account needed):
  - top-level files: participants.tsv, participants.json, dataset_description.json, README
  - for every participant: eyes-closed (ec) and eyes-open (eo) EDF files,
    plus their channels.tsv and eeg.json sidecars.
The Raven's task ("pc") is skipped. Expect about 12-13 GB.

Run:  .venv/bin/python src/download.py [--limit N] [--workers 8]
It is safe to re-run: files that already exist with the right size are skipped.
"""
import argparse
import csv
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DATA, S3_BASE, TASKS  # noqa: E402

TOP_LEVEL = ["participants.tsv", "participants.json",
             "dataset_description.json", "README", "CHANGES"]
SIDECARS = ["eeg.edf", "channels.tsv", "eeg.json"]


def fetch(session: requests.Session, rel: str) -> str:
    """Download one file to DATA/rel unless it is already complete."""
    url = f"{S3_BASE}/{rel}"
    dest = DATA / rel
    head = session.head(url, timeout=60)
    if head.status_code == 404:
        return f"missing {rel}"
    head.raise_for_status()
    size = int(head.headers.get("Content-Length", -1))
    if dest.exists() and dest.stat().st_size == size:
        return "skip"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with session.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.rename(dest)
    return "ok"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="first N participants only")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    session = requests.Session()
    for name in TOP_LEVEL:
        print(name, fetch(session, name))

    with open(DATA / "participants.tsv", encoding="utf-8") as f:
        subjects = [row["participant_id"] for row in csv.DictReader(f, delimiter="\t")]
    if args.limit:
        subjects = subjects[: args.limit]

    rels = [f"{s}/eeg/{s}_task-{t}_{kind}" for s in subjects for t in TASKS for kind in SIDECARS]
    missing = []
    with ThreadPoolExecutor(args.workers) as pool:
        futures = {pool.submit(fetch, session, r): r for r in rels}
        for fut in tqdm(as_completed(futures), total=len(futures), unit="file"):
            try:
                result = fut.result()
            except Exception as exc:  # network hiccup: report and carry on
                result = f"error {futures[fut]}: {exc}"
            if result.startswith(("missing", "error")):
                missing.append(result)

    log = DATA / "download_problems.txt"
    log.write_text("\n".join(missing))
    print(f"{len(subjects)} participants; {len(missing)} problems logged to {log}")


if __name__ == "__main__":
    main()
