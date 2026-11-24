"""Robustness analyses (pre-registered, section 8 of prereg.md).

1. Specification curve: presence rate, IAF-age slope and exponent-age slope
   for every combination of region x fit range x aperiodic mode x peak
   threshold x R^2 floor (3 x 3 x 2 x 6 x 3 = 324 per site).
2. Leave-one-researcher-out: H1 rate and H3/H4 slopes with each cluster dropped.
3. Raw peak pick (Vianney et al., 2025 style): tallest point in 7-12 Hz of the
   raw spectrum, vs specparam IAF.
4. Second-detector agreement: Cohen's kappa between specparam and the SG detector.
5. Null calibration: specparam false-positive rate on simulated aperiodic-only
   spectra whose noise level matches the observed fit error.

Run:  .venv/bin/python src/robustness.py
Outputs: results/spec_curve.csv, results/loro.csv, results/robustness_summary.csv
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from models import covariates, load  # noqa: E402
from prereg_guard import require_prereg  # noqa: E402


def slope(d: pd.DataFrame, y: str, site: str) -> float:
    d = d.dropna(subset=[y, "sex", "quality"])
    if len(d) < 50:
        return np.nan
    return smf.ols(f"{y} ~ {covariates(site)}", d).fit().params["age_dec"]


def spec_curve(base: pd.DataFrame) -> pd.DataFrame:
    grid = pd.read_csv(cfg.RESULTS / "features_grid.csv")
    keep = ["participant_id", "site", "age_dec", "sex", "quality", "researcher_cluster", "montage_family"]
    grid = grid.merge(base[keep], on="participant_id")
    rows = []
    for (site, roi, fr, mode, h), g in grid.groupby(["site", "roi", "fit_range", "mode", "min_peak_height"]):
        for r2 in cfg.GRID["r2_floor"]:
            d = g[g["fit_ok"] & (g["r2"] >= r2)]
            rows.append(dict(site=site, roi=roi, fit_range=fr, mode=mode, min_peak_height=h, r2_floor=r2,
                             n=len(d), presence=d["alpha_present"].mean(),
                             iaf_slope=slope(d[d["alpha_present"]], "iaf", site),
                             exponent_slope=slope(d, "exponent", site)))
    return pd.DataFrame(rows)


def loro(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for site, g in df.groupby("site"):
        for cl in sorted(g["researcher_cluster"].unique()):
            d = g[g["researcher_cluster"] != cl]
            gf = d[d["good_fit"]]
            rows.append(dict(site=site, dropped=cl, n=len(d), presence=d["alpha_present"].mean(),
                             iaf_slope=slope(gf[gf["alpha_present"]], "iaf", site),
                             exponent_slope=slope(gf, "exponent", site)))
    return pd.DataFrame(rows)


def kappa(a: np.ndarray, b: np.ndarray) -> float:
    a, b = a.astype(bool), b.astype(bool)
    po = (a == b).mean()
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return (po - pe) / (1 - pe) if pe < 1 else np.nan


def null_calibration(df: pd.DataFrame, n_sim: int = 500) -> pd.DataFrame:
    """Share of aperiodic-only simulated spectra in which specparam 'finds' alpha."""
    from fooof.sim.gen import gen_power_spectrum
    from fit_specparam import features, fit_one
    rng = np.random.default_rng(2026)
    rows = []
    for site, g in df.groupby("site"):
        g = g[g["fit_ok"]]
        for i in range(n_sim):
            r = g.sample(1, random_state=int(rng.integers(1e9))).iloc[0]
            np.random.seed(int(rng.integers(1e9)))
            f, p = gen_power_spectrum([1, 45], [r["offset"], r["exponent"]], [], nlv=float(r["fit_error"]),
                                      freq_res=0.25)
            rows.append(dict(site=site, false_positive=features(fit_one(f, p)).get("alpha_present", False)))
    return pd.DataFrame(rows).groupby("site")["false_positive"].mean().rename("null_false_positive_rate").reset_index()


def native_128hz_only(g: pd.DataFrame, site: str) -> dict:
    """prereg §5.2: repeat H1 and H3-H5 without the 7 Indian participants recorded at 256 Hz."""
    d = g[g["sfreq"] == 128]
    gf = d[d["good_fit"] & d["alpha_present"]].copy()
    gf["alpha_pw_z"] = (gf["alpha_pw"] - gf["alpha_pw"].mean()) / gf["alpha_pw"].std()
    return dict(n_128hz=len(d), presence_128hz=d["alpha_present"].mean(),
                iaf_slope_128hz=slope(gf, "iaf", site),
                exponent_slope_128hz=slope(d[d["good_fit"]], "exponent", site),
                alpha_power_z_slope_128hz=slope(gf, "alpha_pw_z", site))


def main() -> None:
    print("Pre-registration commit:", require_prereg())
    df = load()
    sc = spec_curve(df)
    sc.to_csv(cfg.RESULTS / "spec_curve.csv", index=False)
    lr = loro(df)
    lr.to_csv(cfg.RESULTS / "loro.csv", index=False)

    summ = []
    for site, g in df.groupby("site"):
        s = sc[sc["site"] == site]
        gf = g[g["good_fit"] & g["alpha_present"]]
        summ.append(dict(site=site,
                         presence_min=s["presence"].min(), presence_median=s["presence"].median(),
                         presence_max=s["presence"].max(),
                         share_specs_presence_above_bar=(s["presence"] > cfg.PRESENCE_BAR).mean(),
                         share_specs_iaf_slope_negative=(s["iaf_slope"] < 0).mean(),
                         share_specs_exponent_slope_negative=(s["exponent_slope"] < 0).mean(),
                         kappa_specparam_vs_sg=kappa(g["alpha_present"].values, g["sg_present"].values),
                         raw_peak_slope=slope(g, "raw_peak_7_12", site),
                         specparam_iaf_slope=slope(gf, "iaf", site),
                         presence_good_fit_only=g.loc[g["good_fit"], "alpha_present"].mean(),
                         **native_128hz_only(g, site)))
    summ = pd.DataFrame(summ).merge(null_calibration(df), on="site")
    summ.to_csv(cfg.RESULTS / "robustness_summary.csv", index=False)
    print(summ.round(3).T)


if __name__ == "__main__":
    main()
