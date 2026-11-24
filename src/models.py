"""Confirmatory models for H1-H5 and the reactivity check V1.

Every model is fitted separately per site. Field researcher enters as a
fixed effect (too few clusters for reliable random effects), data quality as
a covariate, and Holm's correction is applied across the confirmatory
family. See preregistration/prereg.md section 7.

Blocked until the pre-registration is committed.

Run:  .venv/bin/python src/models.py
Output: results/confirmatory.csv (one row per test), results/model_tables.txt,
        results/descriptives.csv
"""
import sys
import warnings
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
# Tests whose pre-registered rule is "one-sided p < .025". Their p-values are doubled
# before Holm's correction so that every test in the family is judged against .05.
ONE_SIDED_025 = ("H1", "H3", "H4")


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


def as_bool(s: pd.Series) -> pd.Series:
    """CSV round trips turn booleans with gaps into strings/objects; missing -> False."""
    return s.map(lambda v: str(v).strip().lower() in ("true", "1", "1.0")).astype(bool)


def load() -> pd.DataFrame:
    meta = pd.read_csv(cfg.RESULTS / "participants_clean.csv")
    qc = pd.read_csv(cfg.RESULTS / "qc_summary.csv")
    ln = pd.read_csv(cfg.RESULTS / "line_noise.csv")
    ft = pd.read_csv(cfg.RESULTS / "features.csv")
    ec = (ft[ft["task"] == "ec"]
          .merge(qc[qc["task"] == "ec"], on=["participant_id", "task"])
          .merge(ln[ln["task"] == "ec"], on=["participant_id", "task"], how="left")
          .merge(meta, on="participant_id"))
    ec = ec[as_bool(ec["usable"])].copy()
    for col in ("alpha_present", "fit_ok", "sg_present"):
        ec[col] = as_bool(ec[col])
    ec["log_line_noise"] = np.log(ec["line_noise_ratio"])
    ec["quality"] = quality_composite(ec)
    ec["age_dec"] = (ec["age_years"] - ec["age_years"].mean()) / 10
    ec["absent"] = (~ec["alpha_present"]).astype(int)
    ec["good_fit"] = ec["fit_ok"] & (ec["r2"] >= cfg.R2_FLOOR)
    return ec


def wilson(k: int, n: int, alpha: float = 0.05):
    return proportion_confint(k, n, alpha=alpha, method="wilson")


def covariates(site: str, g: pd.DataFrame | None = None, quality: bool = True) -> str:
    """Right-hand side shared by all models. A factor with a single level is dropped."""
    terms = ["age_dec", "C(sex)"] + (["quality"] if quality else []) + ["C(researcher_cluster)"]
    if site == "Tanzania":
        terms.append("C(montage_family)")
    if g is not None:
        for col in ("sex", "researcher_cluster", "montage_family"):
            if col in g and g[col].nunique() < 2:
                terms = [t for t in terms if t != f"C({col})"]
    return " + ".join(terms)


def firth_logit(X: np.ndarray, y: np.ndarray, max_iter: int = 200, tol: float = 1e-8):
    """Firth's bias-reduced logistic regression (Jeffreys-prior penalty).

    Used only as a sensitivity analysis: it stays finite when a predictor
    separates the outcome perfectly, which ordinary maximum likelihood does not.
    Returns (coefficients, standard errors).
    """
    b = np.zeros(X.shape[1])
    for _ in range(max_iter):
        p = 1 / (1 + np.exp(-X @ b))
        w = p * (1 - p)
        info = X.T @ (X * w[:, None])
        inv = np.linalg.pinv(info)
        h = np.einsum("ij,jk,ik->i", X * np.sqrt(w)[:, None], inv, X * np.sqrt(w)[:, None])
        step = inv @ (X.T @ (y - p + h * (0.5 - p)))
        step = np.clip(step, -5, 5)
        b = b + step
        if np.abs(step).max() < tol:
            break
    p = 1 / (1 + np.exp(-X @ b))
    info = X.T @ (X * (p * (1 - p))[:, None])
    return b, np.sqrt(np.diag(np.linalg.pinv(info)))


def _row(test, site, n, est, lo, hi, p, rule, supported, note=""):
    return dict(test=test, site=site, n=int(n), estimate=est, ci_low=lo, ci_high=hi, p=p,
                rule=rule, supported_raw=bool(supported), note=note)


def h1_presence(g, site):
    k, n = int(g["alpha_present"].sum()), len(g)
    lo, hi = wilson(k, n)
    p = stats.binomtest(k, n, cfg.PRESENCE_BAR, alternative="greater").pvalue
    return _row("H1 presence", site, n, k / n, lo, hi, p, f"Wilson 95% CI low > {cfg.PRESENCE_BAR}",
                lo > cfg.PRESENCE_BAR)


def h2_absence(g, site, quality=True):
    """Logistic model for a missing peak. Returns (rows, table text)."""
    rows = []
    income = site == "India"
    d = g.dropna(subset=["sex"] + (["quality"] if quality else []) + (["income_rank_z"] if income else []))
    f = "absent ~ " + covariates(site, d, quality) + (" + income_rank_z" if income else "")
    n_abs = int(d["absent"].sum())
    note, m = f"{n_abs} absent of {len(d)}", None
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            m = smf.logit(f, d).fit(disp=False, maxiter=200)
        if any("separation" in str(x.message).lower() or "converge" in str(x.message).lower() for x in w) \
                or not np.isfinite(m.bse).all() or (m.bse > 20).any():
            note += "; ML fit unstable (separation or non-convergence): see the Firth rows"
    except Exception as exc:
        note += f"; ML fit failed ({type(exc).__name__}): see the Firth rows"
    # Firth sensitivity fit on the same design matrix
    import patsy
    yy, XX = patsy.dmatrices(f, d, return_type="dataframe")
    fb, fse = firth_logit(XX.values, yy.values.ravel())
    firth = dict(zip(XX.columns, zip(fb, fse)))

    lb, ub = np.log(cfg.EQUIV_OR_BOUNDS[0]), np.log(cfg.EQUIV_OR_BOUNDS[1])
    if quality:
        if m is not None:
            b, se, p = m.params["quality"], m.bse["quality"], m.pvalues["quality"]
            rows.append(_row("H2a quality -> absence", site, m.nobs, np.exp(b), np.exp(b - 1.96 * se),
                             np.exp(b + 1.96 * se), p, "OR < 1 and two-sided p < .05",
                             (p < .05) and (b < 0), note))
        else:
            rows.append(_row("H2a quality -> absence", site, len(d), np.nan, np.nan, np.nan, np.nan,
                             "OR < 1 and two-sided p < .05", False, note))
        b, se = firth["quality"]
        rows.append(_row("H2a quality -> absence (Firth, sensitivity)", site, len(d), np.exp(b),
                         np.exp(b - 1.96 * se), np.exp(b + 1.96 * se), 2 * stats.norm.sf(abs(b / se)),
                         "not confirmatory", (b < 0) and (2 * stats.norm.sf(abs(b / se)) < .05), note))
    if income:
        def tost(b, se):
            return max(stats.norm.sf((b - lb) / se), stats.norm.cdf((b - ub) / se))
        if m is not None:
            b, se = m.params["income_rank_z"], m.bse["income_rank_z"]
            lo90, hi90 = np.exp(b - 1.645 * se), np.exp(b + 1.645 * se)
            rows.append(_row("H2b income equivalence", site, m.nobs, np.exp(b), lo90, hi90, tost(b, se),
                             "90% CI within 0.80-1.25",
                             (lo90 > cfg.EQUIV_OR_BOUNDS[0]) and (hi90 < cfg.EQUIV_OR_BOUNDS[1]), note))
        else:
            rows.append(_row("H2b income equivalence", site, len(d), np.nan, np.nan, np.nan, np.nan,
                             "90% CI within 0.80-1.25", False, note))
        b, se = firth["income_rank_z"]
        lo90, hi90 = np.exp(b - 1.645 * se), np.exp(b + 1.645 * se)
        rows.append(_row("H2b income equivalence (Firth, sensitivity)", site, len(d), np.exp(b), lo90, hi90,
                         tost(b, se), "not confirmatory",
                         (lo90 > cfg.EQUIV_OR_BOUNDS[0]) and (hi90 < cfg.EQUIV_OR_BOUNDS[1]), note))
    table = f"=== H2 {site} ({'with' if quality else 'without'} quality)\n" + \
            (str(m.summary()) if m is not None else "ML fit failed") + \
            "\nFirth coefficients (log-odds, SE):\n" + \
            "\n".join(f"  {k}: {v[0]:.4f} ({v[1]:.4f})" for k, v in firth.items())
    return rows, table


def h3_h4_h5(g, site, quality=True):
    """OLS with HC3 errors for IAF, exponent and (standardised) alpha power. Returns (rows, tables)."""
    rows, tables = [], []
    gf = g[g["good_fit"]].dropna(subset=["sex"] + (["quality"] if quality else []))
    for test, y, need_peak in [("H3 IAF ~ age", "iaf", True), ("H4 exponent ~ age", "exponent", False)]:
        d = gf[gf["alpha_present"]] if need_peak else gf
        m = smf.ols(f"{y} ~ {covariates(site, d, quality)}", d).fit(cov_type="HC3")
        tables.append(f"=== {test} {site}\n{m.summary()}")
        b, se = m.params["age_dec"], m.bse["age_dec"]
        p1 = float(stats.norm.cdf(b / se))            # one-sided p for slope < 0
        rows.append(_row(test, site, m.nobs, b, b - 1.96 * se, b + 1.96 * se, p1,
                         "slope < 0, one-sided p < .025", (b < 0) and (p1 < .025)))
    d = gf[gf["alpha_present"]].copy()
    d["alpha_pw_z"] = (d["alpha_pw"] - d["alpha_pw"].mean()) / d["alpha_pw"].std()
    m = smf.ols(f"alpha_pw_z ~ {covariates(site, d, quality)}", d).fit(cov_type="HC3")
    tables.append(f"=== H5 alpha power ~ age {site}\n{m.summary()}")
    b, se = m.params["age_dec"], m.bse["age_dec"]
    eq = cfg.EQUIV_STD_SLOPE
    p_tost = max(stats.norm.sf((b + eq) / se), stats.norm.cdf((b - eq) / se))
    rows.append(_row("H5 alpha power equivalence", site, m.nobs, b, b - 1.645 * se, b + 1.645 * se, p_tost,
                     f"90% CI within +/-{eq} SD per decade",
                     (b - 1.645 * se > -eq) and (b + 1.645 * se < eq)))
    return rows, tables


def v1_reactivity(g, site):
    r = g["reactivity_log10"].dropna()
    k, n = int((r > 0).sum()), len(r)
    lo, hi = wilson(k, n)
    return _row("V1 reactivity", site, n, k / n, lo, hi,
                stats.binomtest(k, n, cfg.PRESENCE_BAR, alternative="greater").pvalue,
                f"Wilson 95% CI low > {cfg.PRESENCE_BAR} (not in the Holm family)", lo > cfg.PRESENCE_BAR)


def holm(res: pd.DataFrame) -> pd.DataFrame:
    """Holm correction across the 11 confirmatory tests.

    Tests judged one-sided at .025 have their p doubled first (p_family), so every
    adjusted p-value is compared with .05. supported = raw rule AND Holm-adjusted p < .05.
    """
    res = res.copy()
    confirm = res["test"].str.match(r"H[1-5]") & ~res["test"].str.contains("sensitivity")
    res["p_family"] = np.nan
    one = res["test"].str[:2].isin(ONE_SIDED_025)
    res.loc[confirm, "p_family"] = np.where(one[confirm], np.minimum(1, 2 * res.loc[confirm, "p"]),
                                            res.loc[confirm, "p"])
    # A confirmatory model that could not be fitted stays in the family with p = 1
    # (not supported), so the family always has the pre-registered 11 tests.
    res.loc[confirm & res["p_family"].isna(), "p_family"] = 1.0
    res["p_holm"] = np.nan
    if confirm.any():
        res.loc[confirm, "p_holm"] = multipletests(res.loc[confirm, "p_family"], method="holm")[1]
    res["supported"] = res["supported_raw"]
    res.loc[confirm, "supported"] = res.loc[confirm, "supported_raw"] & (res.loc[confirm, "p_holm"] < cfg.ALPHA_LEVEL)
    return res


def analyse(df: pd.DataFrame, quality: bool = True) -> tuple[pd.DataFrame, list[str]]:
    """All confirmatory tests for both sites. quality=False is the pre-registered
    sensitivity analysis without the quality covariate (prereg section 8.6)."""
    rows, tables = [], []
    for site, g in df.groupby("site"):
        rows.append(h1_presence(g, site))
        r, t = h2_absence(g, site, quality)
        rows += r
        tables.append(t)
        r, t = h3_h4_h5(g, site, quality)
        rows += r
        tables += t
        if "reactivity_log10" in g:
            rows.append(v1_reactivity(g, site))
    return holm(pd.DataFrame(rows)), tables


def descriptives(df: pd.DataFrame) -> pd.DataFrame:
    """Table 1: sample, quality and fit quality by site (eyes-closed, usable recordings)."""
    rows = []
    for site, g in df.groupby("site"):
        rows.append({
            "site": site, "n_usable": len(g), "female_pct": 100 * (g["sex"] == "F").mean(),
            "sex_missing": int(g["sex"].isna().sum()),
            "age_midpoint_median": g["age_years"].median(),
            "age_55plus_pct": 100 * (g["age_years"] >= 55).mean(),
            "clean_sec_median": g["clean_sec"].median(),
            "share_epochs_kept_median": g["share_epochs_kept"].median(),
            "EQ_roi_median": g["EQ_roi"].median(),
            "line_noise_ratio_median": g["line_noise_ratio"].median(),
            "fit_failures": int((~g["fit_ok"]).sum()),
            "r2_median": g["r2"].median(),
            "r2_below_floor": int((g["fit_ok"] & (g["r2"] < cfg.R2_FLOOR)).sum()),
            "alpha_present_pct": 100 * g["alpha_present"].mean(),
            "n_researcher_clusters": g["researcher_cluster"].nunique(),
        })
    return pd.DataFrame(rows)


def run() -> pd.DataFrame:
    df = load()
    res, tables = analyse(df)
    res.to_csv(cfg.RESULTS / "confirmatory.csv", index=False)
    (cfg.RESULTS / "model_tables.txt").write_text("\n\n".join(tables))
    descriptives(df).to_csv(cfg.RESULTS / "descriptives.csv", index=False)
    return res


def main() -> None:
    print("Pre-registration commit:", require_prereg())
    res = run()
    print(res.drop(columns=["rule", "note"]).round(4).to_string(index=False))


if __name__ == "__main__":
    main()
