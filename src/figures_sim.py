"""Figures for the simulation study (no real data).

S1  detection of an alpha peak vs its true height, by recording length:
    specparam (primary settings) and the Savitzky-Golay detector
S2  false "present" rate on recordings with no alpha, by recording length and exponent
S3  recovery: IAF error, exponent error, fitted height vs true height

Run:  .venv/bin/python src/figures_sim.py     (reads results/simulation/exp_A.csv)
Output: paper/figures/figS1_detection.{png,pdf}, figS2_false_present, figS3_recovery
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

SIM = cfg.ROOT / "results" / "simulation"
FIG = cfg.ROOT / "paper" / "figures"
# One hue, light to dark, for the ordered variable (recording length).
LEN_COL = {30: "#b3cde3", 60: "#6baed6", 120: "#2171b5", 180: "#08306b"}
INK, MUTED = "#222222", "#888888"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "savefig.dpi": 300, "savefig.bbox": "tight", "axes.edgecolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.labelcolor": INK,
                     "lines.linewidth": 1.6, "lines.markersize": 4})


def load_A() -> pd.DataFrame:
    d = pd.read_csv(SIM / "exp_A.csv")
    for c in ("alpha_present", "sg_present"):
        d[c] = d[c].astype(str).str.lower().eq("true")
    return d


def save(fig, name):
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIG / f"{name}.{ext}")
    plt.close(fig)


def fig_s1(d):
    fig, axes = plt.subplots(1, 2, figsize=(7, 2.9), sharey=True)
    for ax, col, title in zip(axes, ["alpha_present", "sg_present"],
                              ["specparam, primary settings", "Savitzky-Golay detector"]):
        for sec, g in d.groupby("rec_sec"):
            m = g.groupby("true_alpha_height")[col].mean()
            ax.plot(m.index, 100 * m.values, "o-", color=LEN_COL[int(sec)], label=f"{int(sec)} s")
        ax.axvline(cfg.MIN_PEAK_HEIGHT, color=MUTED, lw=0.8, ls=":")
        ax.set_title(title, fontsize=9, color=INK)
        ax.set_xlabel("True alpha height above the 1/f background (log10)")
        ax.set_ylim(0, 102)
    axes[0].set_ylabel("Recordings with a reported peak (%)")
    axes[0].text(0.0, 4, "true height 0 =\nno alpha", fontsize=7, color=MUTED)
    axes[1].legend(title="Recording length", frameon=False, fontsize=7, title_fontsize=7, loc="lower right")
    save(fig, "figS1_detection")


def fig_s2(d):
    z = d[d["true_alpha_height"] == 0]
    fig, ax = plt.subplots(figsize=(3.8, 2.9))
    for sec, g in z.groupby("rec_sec"):
        m = g.groupby("true_exponent")["alpha_present"].mean()
        ax.plot(m.index, 100 * m.values, "o-", color=LEN_COL[int(sec)], label=f"{int(sec)} s")
    ax.set_xlabel("True aperiodic exponent")
    ax.set_ylabel('False "alpha present" (%)')
    ax.set_ylim(0, 102)
    ax.legend(title="Recording length", frameon=False, fontsize=7, title_fontsize=7)
    save(fig, "figS2_false_present")


def fig_s3(d):
    p = d[(d["true_alpha_height"] >= 0.2) & d["alpha_present"]]
    fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.6))
    for sec, g in p.groupby("rec_sec"):
        m = g.groupby("true_alpha_height").apply(lambda v: (v["iaf"] - v["true_alpha_cf"]).abs().mean())
        axes[0].plot(m.index, m.values, "o-", color=LEN_COL[int(sec)], label=f"{int(sec)} s")
        m = g.groupby("true_alpha_height")["alpha_pw"].mean()
        axes[2].plot(m.index, m.values, "o-", color=LEN_COL[int(sec)])
    for sec, g in d.groupby("rec_sec"):
        m = g.groupby("true_exponent").apply(lambda v: (v["exponent"] - v["true_exponent"]).mean())
        axes[1].plot(m.index, m.values, "o-", color=LEN_COL[int(sec)])
    axes[0].set_xlabel("True alpha height (log10)")
    axes[0].set_ylabel("IAF mean absolute error (Hz)")
    axes[0].set_ylim(bottom=0)
    axes[1].axhline(0, color=MUTED, lw=0.8)
    axes[1].set_xlabel("True exponent")
    axes[1].set_ylabel("Exponent bias (estimate - truth)")
    lim = [0.15, 0.85]
    axes[2].plot(lim, lim, color=MUTED, lw=0.8, ls=":")
    axes[2].set_xlabel("True alpha height (log10)")
    axes[2].set_ylabel("Fitted alpha height (log10)")
    axes[0].legend(title="Recording length", frameon=False, fontsize=7, title_fontsize=7)
    fig.tight_layout()
    save(fig, "figS3_recovery")


def main() -> None:
    d = load_A()
    fig_s1(d)
    fig_s2(d)
    fig_s3(d)
    print("Simulation figures written to", FIG)


if __name__ == "__main__":
    main()
