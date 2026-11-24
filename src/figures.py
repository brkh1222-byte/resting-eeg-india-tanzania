"""Figures 1-6 for the paper (see the research plan, section B5).

1 participant flow by site        4 odds ratios for absence (forest plot)
2 example spectra with fits       5 IAF, exponent, alpha power by age group
3 presence vs peak threshold      6 specification curve

Colour-blind-safe palette; one colour per site throughout.
Run:  .venv/bin/python src/figures.py     Output: paper/figures/fig*.png and .pdf
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as cfg  # noqa: E402
from models import load  # noqa: E402
from prereg_guard import require_prereg  # noqa: E402

SITE_COLOURS = {"India": "#0072B2", "Tanzania": "#D55E00"}   # Okabe-Ito
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 300, "savefig.bbox": "tight"})


def save(fig, name):
    cfg.FIGURES.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(cfg.FIGURES / f"{name}.{ext}")
    plt.close(fig)


def fig1_flow():
    meta = pd.read_csv(cfg.RESULTS / "participants_clean.csv")
    qc = pd.read_csv(cfg.RESULTS / "qc_summary.csv")
    usable = set(qc[(qc["task"] == "ec") & (qc["usable"] == True)]["participant_id"])  # noqa: E712
    steps = []
    for site, g in meta.groupby("site"):
        steps.append([site, len(g), g["adult"].sum(), g["analysable"].sum(), g["participant_id"].isin(usable).sum()])
    t = pd.DataFrame(steps, columns=["site", "All", "Adults, known age", "+ O1 and O2", "+ >=60 s clean EC"])
    fig, ax = plt.subplots(figsize=(6, 2.6))
    x = np.arange(4)
    for i, r in t.iterrows():
        vals = r.iloc[1:].astype(int).values
        ax.bar(x + (i - 0.5) * 0.38, vals, 0.38, color=SITE_COLOURS[r["site"]], label=r["site"])
        for xi, v in zip(x, vals):
            ax.text(xi + (i - 0.5) * 0.38, v + 15, str(v), ha="center", fontsize=7)
    ax.set_xticks(x, t.columns[1:])
    ax.set_ylabel("Participants")
    ax.legend(frameon=False)
    save(fig, "fig1_flow")


def fig2_examples(df):
    from fit_specparam import fit_one, roi_spectrum
    picks = {"Clear peak": df[df["alpha_present"]].nlargest(1, "alpha_pw"),
             "Weak peak": df[df["alpha_present"]].nsmallest(1, "alpha_pw"),
             "No peak": df[~df["alpha_present"].astype(bool)].nlargest(1, "r2")}
    fig, axes = plt.subplots(1, 3, figsize=(7, 2.3), sharey=True)
    for ax, (title, r) in zip(axes, picks.items()):
        if r.empty:
            continue
        r = r.iloc[0]
        z = np.load(cfg.DERIV / "psd" / f"{r['participant_id']}_ec.npz")
        spec = roi_spectrum(z["psd"].astype(float), list(z["ch_names"]), cfg.ROI_PRIMARY)
        fm = fit_one(z["freqs"], spec)
        ax.plot(fm.freqs, fm.power_spectrum, color="0.3", lw=1, label="Spectrum")
        ax.plot(fm.freqs, fm.fooofed_spectrum_, color="#CC79A7", lw=1.2, label="Full fit")
        ax.plot(fm.freqs, fm._ap_fit, color="#009E73", ls="--", lw=1, label="1/f fit")
        ax.set_title(f"{title}\nR² = {fm.r_squared_:.2f}, EQ = {r['EQ_roi']:.1f}", fontsize=8)
        ax.set_xlabel("Frequency (Hz)")
    axes[0].set_ylabel("log10 power")
    axes[0].legend(frameon=False, fontsize=6)
    save(fig, "fig2_examples")


def fig3_threshold():
    sc = pd.read_csv(cfg.RESULTS / "spec_curve.csv")
    d = sc[(sc["roi"] == "O1O2") & (sc["fit_range"] == "2-40") & (sc["mode"] == "fixed") & (sc["r2_floor"] == 0)]
    fig, ax = plt.subplots(figsize=(3.6, 2.8))
    for site, g in d.groupby("site"):
        ax.plot(g["min_peak_height"], 100 * g["presence"], "o-", color=SITE_COLOURS[site], label=site)
    for y, lab in [(97, "Corcoran 2018"), (71.3, "Bhavnani 2022"), (80, "H1 bar")]:
        ax.axhline(y, color="0.6", ls=":", lw=0.8)
        ax.text(0.31, y, lab, fontsize=6, va="center")
    ax.axvline(cfg.MIN_PEAK_HEIGHT, color="0.8", lw=0.8)
    ax.set_xlabel("Minimum peak height (log10 power)")
    ax.set_ylabel("Alpha peak present (%)")
    ax.legend(frameon=False)
    save(fig, "fig3_threshold")


def fig4_forest():
    res = pd.read_csv(cfg.RESULTS / "confirmatory.csv")
    d = res[res["test"].str.startswith("H2")].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(4, 1.8))
    for i, r in d.iterrows():
        ax.errorbar(r["estimate"], i, xerr=[[r["estimate"] - r["ci_low"]], [r["ci_high"] - r["estimate"]]],
                    fmt="o", color=SITE_COLOURS[r["site"]])
    ax.axvspan(*cfg.EQUIV_OR_BOUNDS, color="0.9", zorder=0)
    ax.axvline(1, color="0.5", lw=0.8)
    ax.set_yticks(range(len(d)), [f"{t.replace('H2 ', '')} ({s})" for t, s in zip(d["test"], d["site"])])
    ax.set_xscale("log")
    ax.set_xlabel("Odds ratio for a missing alpha peak (per SD)")
    save(fig, "fig4_forest")


def fig5_age(df):
    gf = df[df["good_fit"]]
    panels = [("iaf", "IAF (Hz)", True), ("exponent", "Aperiodic exponent", False),
              ("alpha_pw", "Alpha power above 1/f (log10)", True)]
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.4))
    for ax, (y, lab, need_peak) in zip(axes, panels):
        d = gf[gf["alpha_present"]] if need_peak else gf
        for site, g in d.groupby("site"):
            m = g.groupby("age_years")[y].agg(["mean", "sem", "size"])
            m = m[m["size"] >= 10]
            ax.errorbar(m.index, m["mean"], yerr=1.96 * m["sem"], fmt="o-", ms=3, color=SITE_COLOURS[site],
                        label=site)
        ax.set_xlabel("Age group midpoint (years)")
        ax.set_ylabel(lab)
    axes[0].legend(frameon=False, fontsize=7)
    save(fig, "fig5_age")


def fig6_spec_curve():
    sc = pd.read_csv(cfg.RESULTS / "spec_curve.csv")
    fig, axes = plt.subplots(3, 1, figsize=(6, 5), sharex=False)
    for ax, (col, lab) in zip(axes, [("presence", "Presence rate"), ("iaf_slope", "IAF slope (Hz/decade)"),
                                     ("exponent_slope", "Exponent slope (/decade)")]):
        for site, g in sc.groupby("site"):
            v = np.sort(g[col].dropna().values)
            ax.plot(np.arange(len(v)), v, ".", ms=2, color=SITE_COLOURS[site], label=site)
        ax.set_ylabel(lab)
        if col != "presence":
            ax.axhline(0, color="0.5", lw=0.8)
    axes[0].axhline(cfg.PRESENCE_BAR, color="0.5", ls=":", lw=0.8)
    axes[-1].set_xlabel("Analysis version (sorted)")
    axes[0].legend(frameon=False, fontsize=7)
    save(fig, "fig6_spec_curve")


def main() -> None:
    require_prereg()
    df = load()
    fig1_flow()
    fig2_examples(df)
    fig3_threshold()
    fig4_forest()
    fig5_age(df)
    fig6_spec_curve()
    print("Figures written to", cfg.FIGURES)


if __name__ == "__main__":
    main()
