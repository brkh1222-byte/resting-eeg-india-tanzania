"""Confirmatory models for H1-H5 and the reactivity check V1.

Every model is fitted separately per site. Field researcher enters as a
fixed effect (9-13 clusters is too few for reliable random effects), data
quality as a covariate, and Holm's correction is applied across the
confirmatory family. See preregistration/prereg.md section 7.

Blocked until the pre-registration is committed.

Run:  .venv/bin/python src/models.py
Output: results/confirmatory.csv (one row per test), results/model_tables.txt
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from prereg_guard import require_prereg  # noqa: E402

QUALITY_VARS = ["EQ_roi", "CQ_roi", "share_epochs_kept", "interpolated_share", "log_line_noise"]


def quality_composite(df: pd.DataFrame) -> pd.Series:
    """First principal component of the z-scored quality metrics, within site.
    Signed so that higher = better quality (positive loading on EQ_roi)."""
    out = pd.Series(np.nan, index=df.index)
    for site, g in df.groupby("site"):
        X = g[QUALITY_VARS].astype(float)
        X = X.loc[:, X.std() > 0]
        X = (X - X.mean()) / X.std()
        X = X.fillna(0.0)
        _, _, vt = np.linalg.svd(X.values, full_matrices=False)
        w = vt[0]
        if "EQ_roi" in X.columns and w[list(X.columns).index("EQ_roi")] < 0:
            w = -w
        pc = X.values @ w
        out.loc[g.index] = (pc - pc.mean()) / pc.std()
    return out


def load() -> pd.DataFrame:
    meta = pd.read_csv(cfg.RESULTS / "participants_clean.csv")
    qc = pd.read_csv(cfg.RESULTS / "qc_summary.csv")
    ln = pd.read_csv(cfg.RESULTS / "line_noise.csv")
    ft = pd.read_csv(cfg.RESULTS / "features.csv")
    ec = (ft[ft["task"] == "ec"]
          .merge(qc[qc["task"] == "ec"], on=["participant_id", "task"])
          .merge(ln[ln["task"] == "ec"], on=["participant_id", "task"], how="left")
          .merge(meta, on="participant_id"))
    ec = ec[ec["usable"] == True].copy()  # noqa: E712
    ec["log_line_noise"] = np.log(ec["line_noise_ratio"])
    ec["quality"] = quality_composite(ec)
    ec["age_dec"] = (ec["age_years"] - ec["age_years"].mean()) / 10
    ec["absent"] = (~ec["alpha_present"].astype(bool)).astype(int)
    ec["good_fit"] = ec["r2"] >= cfg.R2_FLOOR
    return ec


def wilson(k: int, n: int, alpha: float = 0.05):
    return proportion_confint(k, n, alpha=alpha, method="wilson")


def covariates(site: str) -> str:
    extra = " + C(montage_family)" if site == "Tanzania" else ""
    return f"age_dec + C(sex) + quality + C(researcher_cluster){extra}"


def main() -> None:
    print("Pre-registration commit:", require_prereg())
    df = load()
    rows, tables = [], []

    for site, g in df.groupby("site"):
        # ---- H1 presence (all usable recordings; no fit-quality exclusion)
        k, n = int(g["alpha_present"].sum()), len(g)
        lo, hi = wilson(k, n)
        p = stats.binomtest(k, n, cfg.PRESENCE_BAR, alternative="greater").pvalue
        rows.append(dict(test="H1 presence", site=site, n=n, estimate=k / n, ci_low=lo, ci_high=hi,
                         p=p, rule=f"CI low > {cfg.PRESENCE_BAR}", supported=lo > cfg.PRESENCE_BAR))

        # ---- H2 absence ~ quality (+ income in India)
        f = "absent ~ quality + " + covariates(site).replace(" + quality", "")
        if site == "India":
            f += " + income_rank_z"
        d = g.dropna(subset=["sex", "quality"] + (["income_rank_z"] if site == "India" else []))
        m = smf.logit(f, d).fit(disp=False)
        tables.append(f"=== H2 {site}\n{m.summary()}")
        b, se = m.params["quality"], m.bse["quality"]
        rows.append(dict(test="H2 quality -> absence", site=site, n=int(m.nobs), estimate=np.exp(b),
                         ci_low=np.exp(b - 1.96 * se), ci_high=np.exp(b + 1.96 * se), p=m.pvalues["quality"],
                         rule="p < .05 (OR < 1: better quality, fewer absences)",
                         supported=(m.pvalues["quality"] < .05) and (b < 0)))
        if site == "India":
            b, se = m.params["income_rank_z"], m.bse["income_rank_z"]
            lo90, hi90 = np.exp(b - 1.645 * se), np.exp(b + 1.645 * se)
            lb, ub = np.log(cfg.EQUIV_OR_BOUNDS[0]), np.log(cfg.EQUIV_OR_BOUNDS[1])
            p_tost = max(1 - stats.norm.cdf((b - lb) / se), stats.norm.cdf((b - ub) / se))
            rows.append(dict(test="H2 income equivalence", site=site, n=int(m.nobs), estimate=np.exp(b),
                             ci_low=lo90, ci_high=hi90, p=p_tost, rule="90% CI within 0.80-1.25",
                             supported=(lo90 > cfg.EQUIV_OR_BOUNDS[0]) and (hi90 < cfg.EQUIV_OR_BOUNDS[1])))

        # ---- H3 IAF, H4 exponent (good fits only); H5 alpha power equivalence
        gf = g[g["good_fit"]].dropna(subset=["sex", "quality"])
        for test, y, need_peak in [("H3 IAF ~ age", "iaf", True), ("H4 exponent ~ age", "exponent", False)]:
            d = gf[gf["alpha_present"]] if need_peak else gf
            m = smf.ols(f"{y} ~ {covariates(site)}", d).fit(cov_type="HC3")
            tables.append(f"=== {test} {site}\n{m.summary()}")
            b, se = m.params["age_dec"], m.bse["age_dec"]
            p1 = m.pvalues["age_dec"] / 2 if b < 0 else 1 - m.pvalues["age_dec"] / 2
            rows.append(dict(test=test, site=site, n=int(m.nobs), estimate=b, ci_low=b - 1.96 * se,
                             ci_high=b + 1.96 * se, p=p1, rule="slope < 0, one-sided p < .025",
                             supported=(b < 0) and (p1 < .025)))
        d = gf[gf["alpha_present"]].copy()
        d["alpha_pw_z"] = (d["alpha_pw"] - d["alpha_pw"].mean()) / d["alpha_pw"].std()
        m = smf.ols(f"alpha_pw_z ~ {covariates(site)}", d).fit(cov_type="HC3")
        tables.append(f"=== H5 alpha power ~ age {site}\n{m.summary()}")
        b, se = m.params["age_dec"], m.bse["age_dec"]
        eq = cfg.EQUIV_STD_SLOPE
        p_tost = max(1 - stats.norm.cdf((b + eq) / se), stats.norm.cdf((b - eq) / se))
        rows.append(dict(test="H5 alpha power equivalence", site=site, n=int(m.nobs), estimate=b,
                         ci_low=b - 1.645 * se, ci_high=b + 1.645 * se, p=p_tost,
                         rule=f"90% CI within +/-{eq} SD per decade",
                         supported=(b - 1.645 * se > -eq) and (b + 1.645 * se < eq)))

        # ---- V1 reactivity (secondary; not in the Holm family)
        r = g["reactivity_log10"].dropna()
        k, n = int((r > 0).sum()), len(r)
        lo, hi = wilson(k, n)
        rows.append(dict(test="V1 reactivity", site=site, n=n, estimate=k / n, ci_low=lo, ci_high=hi,
                         p=stats.binomtest(k, n, cfg.PRESENCE_BAR, alternative="greater").pvalue,
                         rule=f"CI low > {cfg.PRESENCE_BAR}", supported=lo > cfg.PRESENCE_BAR))

    res = pd.DataFrame(rows)
    fam = ~res["test"].str.startswith("V1")
    res["p_holm"] = np.nan
    res.loc[fam, "p_holm"] = multipletests(res.loc[fam, "p"], method="holm")[1]
    res.to_csv(cfg.RESULTS / "confirmatory.csv", index=False)
    (cfg.RESULTS / "model_tables.txt").write_text("\n\n".join(tables))
    print(res.round(4).to_string(index=False))


if __name__ == "__main__":
    main()
