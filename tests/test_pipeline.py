"""Tests on SIMULATED data only. Nothing here reads the real recordings.

Run:  .venv/bin/python -m pytest tests -q            (fast tests, about 1 minute)
      .venv/bin/python -m pytest tests -q -m slow    (simulated end-to-end run, several minutes)
"""
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import config as C  # noqa: E402
import fit_specparam as F  # noqa: E402
import models as M  # noqa: E402
import preprocess as P  # noqa: E402
import simulate as S  # noqa: E402

PY = sys.executable


def test_guard_blocks_real_spectra_until_prereg_is_committed():
    """While prereg.md is a draft or uncommitted, every spectral script must refuse to run."""
    prereg = ROOT / "preregistration" / "prereg.md"
    tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files", "preregistration/prereg.md"],
                             capture_output=True, text=True).stdout.strip()
    if tracked and "STATUS: DRAFT" not in prereg.read_text(encoding="utf-8"):
        pytest.skip("pre-registration is committed; the gate is open")
    env = {k: v for k, v in os.environ.items() if k != "ALPHA_SIM_ROOT"}
    for script in ("psd.py", "fit_specparam.py", "models.py", "robustness.py", "figures.py"):
        r = subprocess.run([PY, "-W", "ignore", str(ROOT / "src" / script)], capture_output=True, text=True, env=env)
        assert r.returncode != 0 and "Pre-registration gate" in r.stderr, script


def test_guard_also_blocks_in_simulation_mode(tmp_path):
    """Setting ALPHA_SIM_ROOT must not open the gate of the main() entry points."""
    prereg = ROOT / "preregistration" / "prereg.md"
    if "STATUS: DRAFT" not in prereg.read_text(encoding="utf-8"):
        pytest.skip("pre-registration is no longer a draft")
    env = {**os.environ, "ALPHA_SIM_ROOT": str(tmp_path)}
    r = subprocess.run([PY, "-W", "ignore", str(ROOT / "src" / "psd.py")], capture_output=True, text=True, env=env)
    assert r.returncode != 0 and "Pre-registration gate" in r.stderr


def test_sim_root_cannot_be_the_repository():
    env = {**os.environ, "ALPHA_SIM_ROOT": str(ROOT / "results")}
    r = subprocess.run([PY, "-c", "import sys; sys.path.insert(0, 'src'); import config"],
                       capture_output=True, text=True, env=env, cwd=ROOT)
    assert r.returncode != 0 and "ALPHA_SIM_ROOT" in r.stderr


def test_recording_without_occipital_channels_does_not_crash():
    """Regression: the 'bitwise_and' error on sub-KAGU1058 eyes-open (no O1/O2)."""
    rng = np.random.default_rng(0)
    x = S.synthesise(S.Truth(), 30, 128.0, rng, n_channels=2)
    raw, aux = P.prepare(S.make_raw(x, 128.0, ["AF3", "AF4"]))
    starts, keep, info = P.accepted_epochs(raw, aux)
    assert keep.dtype == bool and keep.all() and np.isnan(info["roi_sd_uv"])


def test_flagged_and_noisy_epochs_are_rejected():
    rng = np.random.default_rng(1)
    x = S.synthesise(S.Truth(), 120, 128.0, rng)
    x[:, 128 * 40:128 * 44] *= 30                       # a 4 s burst
    flag = np.zeros(x.shape[1])
    flag[128 * 100] = 1                                 # one flagged sample
    raw, aux = P.prepare(S.make_raw(x, 128.0, ["O1", "O2"], flag))
    starts, keep, _ = P.accepted_epochs(raw, aux)
    bad = [i for i, s in enumerate(starts) if (s < 128 * 44 and s + 512 > 128 * 40) or (s <= 128 * 100 < s + 512)]
    assert not keep[bad].any() and keep.sum() >= len(starts) - len(bad) - 3


def test_synthesised_spectrum_matches_the_truth():
    """Mean-Welch spectrum of a simulated recording follows offset - exponent*log10(f) + peak."""
    rng = np.random.default_rng(2)
    t = S.Truth(exponent=1.5, offset=1.0, alpha_height=0.5, alpha_cf=10, alpha_sd=1.0)
    f, p, _ = S.pipeline_spectrum(S.synthesise(t, 600, 128.0, rng), 128.0, average="mean")
    lp = np.log10(p.mean(axis=0))
    m = ((f >= 2) & (f <= 6)) | ((f >= 16) & (f <= 40))
    slope, icpt = np.polyfit(np.log10(f[m]), lp[m], 1)
    assert abs(-slope - 1.5) < 0.05 and abs(icpt - 1.0) < 0.05
    at10 = lp[np.argmin(abs(f - 10))] - (icpt + slope * 1.0)
    assert abs(at10 - 0.5) < 0.1


@pytest.mark.parametrize("exponent", [0.7, 1.2, 1.8])
def test_strong_alpha_is_found_and_parameters_recovered(exponent):
    rng = np.random.default_rng(3)
    hits, iaf_err, exp_err = 0, [], []
    for _ in range(8):
        r = S.simulate_and_fit(S.Truth(exponent=exponent, alpha_height=0.6, alpha_cf=rng.uniform(8.5, 11.5)),
                               clean_sec=120, rng=rng)
        hits += r["alpha_present"]
        iaf_err.append(abs(r["iaf"] - r["true_alpha_cf"]))
        exp_err.append(abs(r["exponent"] - exponent))
    assert hits == 8
    assert np.nanmedian(iaf_err) < 0.3
    assert np.median(exp_err) < 0.15


def test_failed_fit_counts_as_no_peak():
    out = F.features(None)
    assert out["fit_ok"] is False and out["alpha_present"] is False


def test_as_bool_handles_csv_round_trip():
    s = pd.Series([True, "True", "False", np.nan, None, 1.0, 0.0])
    assert M.as_bool(s).tolist() == [True, True, False, False, False, True, False]


def test_firth_matches_ml_on_easy_data_and_survives_separation():
    import statsmodels.api as sm
    rng = np.random.default_rng(4)
    X = sm.add_constant(rng.standard_normal((2000, 2)))
    y = (rng.random(2000) < 1 / (1 + np.exp(-(X @ [-1.0, 0.8, 0.0])))).astype(float)
    b, se = M.firth_logit(X, y)
    ml = sm.Logit(y, X).fit(disp=False)
    assert np.allclose(b, ml.params, atol=0.03) and np.allclose(se, ml.bse, rtol=0.05)
    Xs = sm.add_constant(np.r_[np.zeros(20), np.ones(20)])      # perfectly separated
    bs, ses = M.firth_logit(Xs, np.r_[np.zeros(20), np.ones(20)])
    assert np.isfinite(bs).all() and np.isfinite(ses).all() and bs[1] > 0


def test_holm_family_and_decision_column():
    rows = [M._row(f"{t}", "India", 100, 0, 0, 0, p, "", True) for t, p in
            [("H1 presence", 0.001), ("H2a quality -> absence", 0.04), ("H3 IAF ~ age", 0.02),
             ("H2a quality -> absence (Firth, sensitivity)", 0.5), ("V1 reactivity", 0.9)]]
    res = M.holm(pd.DataFrame(rows)).set_index("test")
    assert res.loc["H1 presence", "p_family"] == pytest.approx(0.002)        # one-sided .025 rule -> doubled
    assert res.loc["H3 IAF ~ age", "p_family"] == pytest.approx(0.04)
    assert res.loc["H1 presence", "p_holm"] == pytest.approx(0.006)
    assert res.loc["H2a quality -> absence", "p_holm"] == pytest.approx(0.08)
    assert bool(res.loc["H1 presence", "supported"]) and not bool(res.loc["H2a quality -> absence", "supported"])
    assert np.isnan(res.loc["V1 reactivity", "p_holm"]) and bool(res.loc["V1 reactivity", "supported"])
    assert np.isnan(res.loc["H2a quality -> absence (Firth, sensitivity)", "p_holm"])


def test_equivalence_logic_on_a_simulated_table():
    """H5-style TOST: a true zero slope with tight SE is 'equivalent'; a planted slope is not."""
    rng = np.random.default_rng(5)
    n = 3000
    d = pd.DataFrame({"site": "India", "age_dec": rng.normal(0, 1.4, n), "sex": rng.choice(["F", "M"], n),
                      "quality": rng.normal(size=n), "researcher_cluster": rng.choice(list("ABCD"), n),
                      "alpha_present": True, "good_fit": True, "iaf": 10 + rng.normal(0, 1, n),
                      "exponent": 1.2 + rng.normal(0, .3, n)})
    d["alpha_pw"] = rng.normal(0.5, 0.2, n)
    rows, _ = M.h3_h4_h5(d, "India")
    assert rows[2]["supported_raw"]
    d["alpha_pw"] += 0.06 * d["age_dec"]                 # 0.3 SD per decade
    rows, _ = M.h3_h4_h5(d, "India")
    assert not rows[2]["supported_raw"]
    d["iaf"] -= 0.2 * d["age_dec"]
    rows, _ = M.h3_h4_h5(d, "India")
    assert rows[0]["supported_raw"] and rows[0]["estimate"] == pytest.approx(-0.2, abs=0.05)


@pytest.mark.slow
def test_simulated_cohort_end_to_end(tmp_path):
    """fit_specparam -> models -> robustness -> figures on a small simulated cohort."""
    env = {**os.environ, "ALPHA_SIM_SMALL_GRID": "1"}
    r = subprocess.run([PY, "-W", "ignore", str(ROOT / "src" / "simulate.py"), "cohort", "--root", str(tmp_path),
                        "--n-per-site", "70"], capture_output=True, text=True, env=env)
    assert r.returncode == 0, r.stderr[-3000:]
    res = tmp_path / "results"
    for name in ("features.csv", "features_grid.csv", "fit_failures.csv", "confirmatory.csv", "model_tables.txt",
                 "descriptives.csv", "spec_curve.csv", "loro.csv", "robustness_summary.csv",
                 "sensitivity_no_quality.csv", "recovery.csv"):
        assert (res / name).exists(), name
    for i in range(1, 7):
        assert list((tmp_path / "paper" / "figures").glob(f"fig{i}_*.png")), f"figure {i}"
    conf = pd.read_csv(res / "confirmatory.csv")
    main = conf[conf["test"].str.match(r"H[1-5]") & ~conf["test"].str.contains("sensitivity")]
    assert len(main) == 11 and main["p_holm"].notna().all()
    rec = pd.read_csv(res / "recovery.csv").set_index(["site", "quantity"])["estimate"]
    for site in ("India", "Tanzania"):
        assert rec[(site, "false 'absent' among planted alpha")] < 0.10
        assert rec[(site, "IAF mean abs error (Hz)")] < 0.5
    # nothing may be written into the repository's own results
    if "STATUS: DRAFT" in (ROOT / "preregistration" / "prereg.md").read_text(encoding="utf-8"):
        assert not (ROOT / "results" / "features.csv").exists()
