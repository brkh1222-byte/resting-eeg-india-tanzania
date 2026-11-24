"""Clean participants.tsv and build a per-recording montage table.

This step uses metadata only (participants.tsv and channels.tsv files).
It computes NO spectra, so it is allowed before the pre-registration
commit (TASKS.md T1.2).

Outputs (results/, committed):
  participants_clean.csv  one row per participant, with:
      site, age_group (fixed), age_years (bin midpoint), adult flag,
      sex (fixed), income_usd, income_rank_within_site (India only),
      researcher (ID prefix, small groups merged), montage family,
      has_O1O2, has_posterior4, analysable flag
  montage_census.csv      counts of each distinct montage by site
"""
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C  # noqa: E402


def eeg_channels(channels_tsv: Path) -> list[str]:
    """EEG electrode names in a channels.tsv (drops timestamps, quality, markers)."""
    if not channels_tsv.exists():
        return []
    names = pd.read_csv(channels_tsv, sep="\t", encoding="utf-8-sig")["name"].astype(str)
    return [n for n in names
            if n not in C.NON_EEG_NAMES and not n.startswith(C.NON_EEG_PREFIXES)]


def researcher_from_id(pid: str) -> str:
    """Letters of the subject ID after 'sub-' (assumed to be the field researcher)."""
    return "".join(ch for ch in pid[4:] if ch.isalpha())


# Income bins in participants.tsv are strings; order them for a within-site rank.
INDIA_INCOME_ORDER = ["<1250", "1250-3750", "3750-6250", "6250-10000", "10000-15000",
                      "15000-25000", "25000-50000", ">50000"]


def main() -> None:
    df = pd.read_csv(C.DATA / "participants.tsv", sep="\t", dtype=str).fillna("n/a")
    df["age_group"] = df["age_group"].replace(C.AGE_GROUP_FIXES)
    df["sex"] = df["sex"].replace(C.SEX_FIXES).replace({"n/a": np.nan})
    df["adult"] = df["age_group"].isin(C.ADULT_AGE_GROUPS)
    df["age_years"] = df["age_group"].map(C.AGE_MIDPOINTS)

    # Montage from the eyes-closed channels file.
    montages, has_o, has_p4 = [], [], []
    for pid in df["participant_id"]:
        chans = eeg_channels(C.DATA / pid / "eeg" / f"{pid}_task-ec_channels.tsv")
        montages.append(",".join(sorted(chans)))
        has_o.append(set(C.ROI_PRIMARY) <= set(chans))
        has_p4.append(set(C.ROI_POSTERIOR4) <= set(chans))
    df["montage"] = montages
    df["has_O1O2"] = has_o
    df["has_posterior4"] = has_p4

    # Montage family: the 3 most common montages per site get names, the rest "other".
    df["montage_family"] = "other"
    for site, g in df.groupby("site"):
        for i, (m, _) in enumerate(Counter(g["montage"]).most_common(3)):
            df.loc[(df["site"] == site) & (df["montage"] == m), "montage_family"] = f"{site[:2]}{i + 1}"

    # Researcher cluster; groups with < MIN_CLUSTER_SIZE analysable people -> "other".
    df["researcher"] = df["participant_id"].map(researcher_from_id)
    df["analysable"] = df["adult"] & df["has_O1O2"]
    sizes = df[df["analysable"]].groupby("researcher").size()
    small = set(sizes[sizes < C.MIN_CLUSTER_SIZE].index)
    df["researcher_cluster"] = df["researcher"].where(~df["researcher"].isin(small), "other")

    # Income: ordered rank within India only (Tanzanian income has almost no spread).
    df["income_ord"] = np.nan
    india = df["site"] == "India"
    df.loc[india, "income_ord"] = df.loc[india, "income_usd"].map(
        {b: i for i, b in enumerate(INDIA_INCOME_ORDER)})
    df["income_rank_z"] = np.nan
    ok = india & df["income_ord"].notna() & df["analysable"]
    r = df.loc[ok, "income_ord"].rank(pct=True)
    df.loc[ok, "income_rank_z"] = (r - r.mean()) / r.std()

    C.RESULTS.mkdir(exist_ok=True)
    keep = ["participant_id", "site", "age_group", "age_years", "adult", "sex",
            "income_usd", "income_ord", "income_rank_z", "mhq_score", "researcher",
            "researcher_cluster", "montage_family", "has_O1O2", "has_posterior4",
            "analysable"]
    df[keep].to_csv(C.RESULTS / "participants_clean.csv", index=False)

    census = (df.groupby(["site", "montage"]).size().rename("n").reset_index()
              .sort_values(["site", "n"], ascending=[True, False]))
    census["n_channels"] = census["montage"].str.count(",") + 1
    census.to_csv(C.RESULTS / "montage_census.csv", index=False)

    # Console summary
    for site, g in df.groupby("site"):
        print(f"{site}: n={len(g)} adults={g['adult'].sum()} "
              f"adult+O1O2={g['analysable'].sum()} posterior4={g['has_posterior4'].sum()} "
              f"montages={g['montage'].nunique()} clusters={g.loc[g['analysable'], 'researcher_cluster'].nunique()}")


if __name__ == "__main__":
    main()
