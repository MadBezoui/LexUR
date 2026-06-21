"""Generate the data-driven figures for the manuscript from results/tables/*.

All figures are vector PDFs written into ../../paper/ (and ../../results/figures/).
Every number is read from the frozen results tables; nothing is hard-coded except
cosmetic styling. LUR is highlighted consistently in crimson.
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
TAB = os.path.abspath(os.path.join(HERE, "..", "..", "results", "tables"))
OUT_DIRS = [
    os.path.abspath(os.path.join(HERE, "..", "..", "paper")),
    os.path.abspath(os.path.join(HERE, "..", "..", "results", "figures")),
]

plt.rcParams.update({
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
    "savefig.bbox": "tight",
    "axes.titlesize": 11,
})

LUR_C = "#c0392b"      # crimson for LUR
BASE_C = "#34495e"     # slate for others
ACC_C = "#2980b9"      # blue accent
GOOD_C = "#27ae60"     # green


def save(fig, name):
    for d in OUT_DIRS:
        if os.path.isdir(d):
            fig.savefig(os.path.join(d, name))
    plt.close(fig)
    print("wrote", name)


def _colors(methods):
    return [LUR_C if m == "LUR" else BASE_C for m in methods]


# ---------------------------------------------------------------- 1. tradeoff
def fig_tradeoff():
    df = pd.read_csv(f"{TAB}/main_comparison.csv")
    # manual label offsets (points) to de-overlap the robust-method cluster
    off = {"CP": (-30, -2), "TOPSIS": (4, 7), "ASF": (8, -3),
           "MMR": (-40, -6), "LUR": (9, -10), "Knee": (7, 4),
           "RW": (6, -12), "SMAA": (4, 6)}
    fig, ax = plt.subplots(figsize=(5.6, 4.2))
    for _, r in df.iterrows():
        is_lur = r["method"] == "LUR"
        ax.scatter(r["loss_mean"], r["tail_loss"],
                   s=150 if is_lur else 70,
                   color=LUR_C if is_lur else BASE_C,
                   zorder=3, edgecolor="white", linewidth=0.8)
        ax.annotate(r["method"],
                    (r["loss_mean"], r["tail_loss"]),
                    textcoords="offset points",
                    xytext=off.get(r["method"], (7, 4)),
                    fontsize=9, fontweight="bold" if is_lur else "normal",
                    color=LUR_C if is_lur else "black")
    ax.set_xlabel("Mean held-out loss  (average case)")
    ax.set_ylabel("Tail held-out loss  CVaR$_{10\\%}$  (worst case)")
    ax.set_title("Average- vs worst-case loss across selection rules")
    ax.grid(True, alpha=0.25)

    # --- zoom inset on the robust-method cluster (lower-left) ---
    from mpl_toolkits.axes_grid1.inset_locator import mark_inset
    axin = ax.inset_axes([0.46, 0.30, 0.50, 0.45])
    cluster = ["CP", "ASF", "MMR", "LUR", "TOPSIS"]
    coff = {"CP": (6, -3), "ASF": (6, 4), "MMR": (-30, -10),
            "LUR": (7, 4), "TOPSIS": (-10, 8)}
    for _, r in df[df["method"].isin(cluster)].iterrows():
        is_lur = r["method"] == "LUR"
        axin.scatter(r["loss_mean"], r["tail_loss"], s=130 if is_lur else 60,
                     color=LUR_C if is_lur else BASE_C, zorder=3,
                     edgecolor="white", linewidth=0.7)
        axin.annotate(r["method"], (r["loss_mean"], r["tail_loss"]),
                      textcoords="offset points", xytext=coff[r["method"]],
                      fontsize=8, fontweight="bold" if is_lur else "normal",
                      color=LUR_C if is_lur else "black")
    axin.set_xlim(0.20, 0.255); axin.set_ylim(0.462, 0.55)
    axin.grid(True, alpha=0.25); axin.tick_params(labelsize=7)
    axin.set_title("robust cluster (zoom)", fontsize=8)
    mark_inset(ax, axin, loc1=2, loc2=3, fc="none", ec="0.6", lw=0.8)
    save(fig, "fig_tradeoff.pdf")


# ------------------------------------------------------------ 2. per-family heatmap
def fig_perfamily():
    df = pd.read_csv(f"{TAB}/per_family_concave_m8.csv").set_index("method")
    fams = ["linear", "chebyshev", "aug_asf", "ces", "choquet", "satisfice", "overall"]
    labels = ["linear", "Chebyshev", "aug. ASF", "CES", "Choquet", "satisfice", "overall"]
    M = df.loc[:, fams].values
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    im = ax.imshow(M, cmap="RdYlGn_r", aspect="auto")
    ax.set_xticks(range(len(fams)), labels, rotation=30, ha="right")
    ax.set_yticks(range(len(df.index)), df.index)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center",
                    fontsize=8, color="black")
    # mark LUR row
    if "LUR" in df.index:
        yi = list(df.index).index("LUR")
        ax.add_patch(plt.Rectangle((-0.5, yi - 0.5), len(fams), 1, fill=False,
                                   edgecolor=LUR_C, lw=2.2))
    ax.set_title("Held-out loss by preference family (concave, $m=8$); lower is better")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02, label="loss")
    save(fig, "fig_perfamily.pdf")


# ----------------------------------------------------------------- 3. redundancy
def fig_redundancy():
    df = pd.read_csv(f"{TAB}/redundancy.csv")
    x = np.arange(len(df)); w = 0.38
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    ax.bar(x - w/2, df["grouped_loss"], w, yerr=df["grouped_std"], capsize=3,
           color=_colors(df["method"]), label="grouped loss")
    ax.bar(x + w/2, df["tail_loss"], w, color=[ACC_C]*len(df), alpha=0.55,
           label="tail loss")
    ax.set_xticks(x, df["method"], rotation=0)
    ax.set_ylabel("loss (lower is better)")
    ax.set_title("Robustness to redundant criteria (grouped vs tail loss)")
    ax.legend(frameon=False)
    ax.grid(True, axis="y", alpha=0.25)
    save(fig, "fig_redundancy.pdf")


# -------------------------------------------------------------- 4. nadir sensitivity
def fig_nadir():
    df = pd.read_csv(f"{TAB}/sensitivity_nadir.csv").sort_values("nadir_err")
    fig, ax1 = plt.subplots(figsize=(6.2, 4.0))
    x = df["nadir_err"] * 100
    ax1.plot(x, df["loss"], "o-", color=GOOD_C, lw=2, label="held-out loss")
    ax1.set_xlabel("nadir estimation error (%)")
    ax1.set_ylabel("held-out loss", color=GOOD_C)
    ax1.tick_params(axis="y", labelcolor=GOOD_C)
    ax1.set_ylim(0, max(df["loss"]) * 1.4)
    ax2 = ax1.twinx()
    ax2.spines["top"].set_visible(False)
    ax2.plot(x, df["flip_rate"] * 100, "s--", color=LUR_C, lw=2, label="winner flip rate")
    ax2.set_ylabel("winner flip rate (%)", color=LUR_C)
    ax2.tick_params(axis="y", labelcolor=LUR_C)
    ax2.set_ylim(0, 100)
    ax1.set_title("Nadir sensitivity: quality is stable, identity is not")
    save(fig, "fig_nadir.pdf")


# ------------------------------------------------------------- 5. probe reduction
def fig_probe_reduction():
    df = pd.read_csv(f"{TAB}/probe_reduction.csv")
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.plot(df["m"], df["full_coalitions"], "o-", color=BASE_C, lw=2,
            label="full coalition family $2(2^m-1)-m$")
    ax.plot(df["m"], df["cluster_probes"], "s-", color=LUR_C, lw=2,
            label="adaptive family $O(m+c)$")
    ax.set_yscale("log")
    ax.set_xlabel("number of criteria $m$")
    ax.set_ylabel("probe-family size (log scale)")
    ax.set_title("Adaptive probe construction keeps the family linear")
    for _, r in df.iterrows():
        ax.annotate(f"{r['reduction']:.0f}$\\times$",
                    (r["m"], r["full_coalitions"]),
                    textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=8, color=BASE_C)
    ax.legend(frameon=False, loc="upper left")
    ax.grid(True, which="both", alpha=0.2)
    save(fig, "fig_probe_reduction.pdf")


# ----------------------------------------------------------------- 6. ablation
def fig_ablation():
    df = pd.read_csv(f"{TAB}/ablation_concave_m8.csv")
    # de-duplicate identical configs but keep informative ones, preserve order
    order = ["Full LUR", "No singletons", "Max only"]
    df = df[df["config"].isin(order)].set_index("config").loc[order].reset_index()
    x = np.arange(len(df)); w = 0.38
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    b1 = ax.bar(x - w/2, df["loss_mean"], w, yerr=df["loss_std"], capsize=3,
                color=ACC_C, label="mean held-out loss")
    b2 = ax.bar(x + w/2, df["wcr_mean"], w, color=LUR_C, alpha=0.8,
                label="worst-case certificate regret")
    ax.set_xticks(x, df["config"])
    ax.set_ylabel("value (lower is better)")
    ax.set_title("Ablation: singletons and the leximax both matter")
    ax.legend(frameon=False)
    ax.grid(True, axis="y", alpha=0.25)
    ax.annotate("max-only lowers loss\nbut inflates regret",
                (2 + w/2, df["wcr_mean"].iloc[2]),
                textcoords="offset points", xytext=(-10, -38), fontsize=8,
                color=LUR_C, ha="center",
                arrowprops=dict(arrowstyle="->", color=LUR_C, lw=1))
    save(fig, "fig_ablation.pdf")


# ------------------------------------------------------------ 7. SMAA distinctness
def fig_smaa_distinct():
    df = pd.read_csv(f"{TAB}/agreement_smaa.csv")
    piv_gap = df.pivot(index="geometry", columns="m", values="mean_gap")
    piv_ag = df.pivot(index="geometry", columns="m", values="agreement")
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    im = ax.imshow(piv_gap.values, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(piv_gap.columns)), [f"m={c}" for c in piv_gap.columns])
    ax.set_yticks(range(len(piv_gap.index)), piv_gap.index)
    for i in range(piv_gap.shape[0]):
        for j in range(piv_gap.shape[1]):
            ax.text(j, i,
                    f"gap {piv_gap.values[i, j]:.2f}\nagree {piv_ag.values[i, j]*100:.0f}%",
                    ha="center", va="center", fontsize=7.5, color="white")
    ax.set_title("LUR vs SMAA: different rule, not a re-description")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="mean choice distance")
    save(fig, "fig_smaa_distinct.pdf")


if __name__ == "__main__":
    fig_tradeoff()
    fig_perfamily()
    fig_redundancy()
    fig_nadir()
    fig_probe_reduction()
    fig_ablation()
    fig_smaa_distinct()
    print("all data figures done")
