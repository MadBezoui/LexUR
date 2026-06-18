"""Benchmark orchestration: replicated comparison, ablations, sensitivity,
probe-reduction, plus table (CSV + LaTeX) and figure generation."""
from __future__ import annotations
import os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from . import problems, methods, metrics, stats

GEOMS = ["linear", "concave", "convex", "disconnected"]
MS = [3, 5, 8, 10]
METHOD_ORDER = ["TOPSIS", "CP", "Knee", "RW", "ASF", "SMAA", "MMR", "LUR"]


# --------------------------------------------------------------------------- #
def _select(name, F, rng):
    fn = methods.METHODS[name]
    if name in ("RW", "SMAA", "MMR"):
        return fn(F, rng=rng)
    return fn(F)


def run_benchmark_clean(reps=30, n=300, n_test=250, seed=20240601, outdir="results"):
    """Replicated out-of-class loss for every method x geometry x m.
    The held-out test-utility draw is identical across methods within a
    replication, so comparisons are paired."""
    rng_master = np.random.default_rng(seed)
    rows, mean_store, tail_store = [], {}, {}
    for geom in GEOMS:
        for m in MS:
            mmat = np.zeros((reps, len(METHOD_ORDER)))
            tmat = np.zeros((reps, len(METHOD_ORDER)))
            for rep in range(reps):
                rng = np.random.default_rng(rng_master.integers(1 << 31))
                F = problems.make_candidate_set(geom, n, m, rng)
                cache = metrics.precompute_utilities(
                    F, np.random.default_rng(int(rng_master.integers(1 << 31))), n_test)
                sel_rng = np.random.default_rng(int(rng_master.integers(1 << 31)))
                for jm, name in enumerate(METHOD_ORDER):
                    idx = _select(name, F, rng=sel_rng)
                    mmat[rep, jm], tmat[rep, jm] = metrics.loss_from_cache(cache, idx)
            mean_store[(geom, m)] = mmat
            tail_store[(geom, m)] = tmat
            for jm, name in enumerate(METHOD_ORDER):
                mc, tc = mmat[:, jm], tmat[:, jm]
                rows.append(dict(geometry=geom, m=m, method=name,
                                 mean=mc.mean(), std=mc.std(),
                                 tail_mean=tc.mean(), tail_std=tc.std(),
                                 median=float(np.median(mc)),
                                 iqr=float(np.subtract(*np.percentile(mc, [75, 25])))))
    df = pd.DataFrame(rows)
    os.makedirs(f"{outdir}/tables", exist_ok=True)
    df.to_csv(f"{outdir}/tables/benchmark_raw.csv", index=False)
    np.savez(f"{outdir}/tables/loss_store.npz",
             **{f"mean_{g}_{m}": mean_store[(g, m)] for g in GEOMS for m in MS},
             **{f"tail_{g}_{m}": tail_store[(g, m)] for g in GEOMS for m in MS})
    return df, mean_store, tail_store


def _stats_block(store, control="LUR"):
    big = np.vstack(list(store.values()))
    fried_stat, fried_p = stats.friedman(big)
    ranks = stats.average_ranks(big)
    cd = stats.nemenyi_cd(len(METHOD_ORDER), big.shape[0])
    wh = stats.wilcoxon_holm(big, METHOD_ORDER, control=control)
    return dict(friedman_stat=fried_stat, friedman_p=fried_p,
                n_datasets=int(big.shape[0]), cd=cd,
                avg_ranks={n: float(r) for n, r in zip(METHOD_ORDER, ranks)},
                wilcoxon_vs_LUR={n: dict(p_raw=v[0], p_holm=v[1], cliffs_delta=v[2])
                                 for n, v in wh.items()}), ranks, cd


def stats_summary(mean_store, tail_store, outdir="results"):
    """Friedman + Wilcoxon-Holm vs LUR + CD diagram, for BOTH the mean-loss and
    the tail (worst-case) loss.  Tail loss is the headline robustness metric."""
    mean_block, _, _ = _stats_block(mean_store)
    tail_block, tail_ranks, cd = _stats_block(tail_store)
    summary = dict(mean_loss=mean_block, tail_loss=tail_block)
    os.makedirs(f"{outdir}/tables", exist_ok=True)
    with open(f"{outdir}/tables/stats_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    _cd_diagram(tail_ranks, cd, outdir)        # CD diagram on the headline metric
    return summary


def _cd_diagram(ranks, cd, outdir):
    order = np.argsort(ranks)
    names = [METHOD_ORDER[i] for i in order]
    r = ranks[order]
    fig, ax = plt.subplots(figsize=(8, 2.4))
    lo, hi = 1, len(METHOD_ORDER)
    ax.set_xlim(lo - 0.5, hi + 0.5); ax.set_ylim(0, 1)
    ax.hlines(0.75, lo, hi, color="k")
    for i, (nm, rr) in enumerate(zip(names, r)):
        ax.vlines(rr, 0.7, 0.8, color="k")
        ax.text(rr, 0.62, f"{nm}\n{rr:.2f}", ha="center", va="top", fontsize=8)
    ax.plot([lo, lo + cd], [0.92, 0.92], color="crimson", lw=3)
    ax.text(lo + cd / 2, 0.95, f"CD={cd:.2f}", ha="center", fontsize=8, color="crimson")
    ax.axis("off")
    ax.set_title("Average ranks of out-of-class loss (lower = better)", fontsize=9)
    os.makedirs(f"{outdir}/figures", exist_ok=True)
    fig.tight_layout(); fig.savefig(f"{outdir}/figures/cd_diagram.pdf"); plt.close(fig)


REDUNDANCY_CONFIGS = {
    "R1 (5 groups, m=10)": [3, 3, 2, 1, 1],
    "R2 (4 groups, m=10)": [4, 3, 2, 1],
    "R3 (4 groups, m=12)": [5, 4, 2, 1],
    "R4 (3 groups, m=12)": [6, 4, 2],
}


def run_redundancy(reps=30, n=300, n_test=300, seed=909, outdir="results"):
    """Realistic redundant-objective benchmark: held-out preferences are over the
    TRUE underlying criteria.  Reports grouped loss (de-redundification quality)
    and tail loss.  This is where adaptive clustering earns its keep."""
    rng_master = np.random.default_rng(seed)
    rows = {}
    store_grp = {}
    for cfg, sizes in REDUNDANCY_CONFIGS.items():
        for geom in ["linear", "concave", "convex"]:
            gmat = np.zeros((reps, len(METHOD_ORDER)))
            tmat = np.zeros((reps, len(METHOD_ORDER)))
            for rep in range(reps):
                rng = np.random.default_rng(rng_master.integers(1 << 31))
                F, groups, base = problems.make_redundant_set(geom, n, sizes, rng)
                s1 = int(rng_master.integers(1 << 31)); s2 = int(rng_master.integers(1 << 31))
                cache_base = metrics.precompute_utilities(base, np.random.default_rng(s1), n_test)
                cache_F = metrics.precompute_utilities(F, np.random.default_rng(s2), n_test)
                sel_rng = np.random.default_rng(int(rng_master.integers(1 << 31)))
                for jm, name in enumerate(METHOD_ORDER):
                    idx = _select(name, F, rng=sel_rng)
                    gmat[rep, jm] = metrics.loss_from_cache(cache_base, idx)[0]
                    tmat[rep, jm] = metrics.loss_from_cache(cache_F, idx)[1]
            store_grp[(cfg, geom)] = gmat
            for jm, name in enumerate(METHOD_ORDER):
                rows.setdefault(name, {"grp": [], "tail": []})
                rows[name]["grp"].append(gmat[:, jm].mean())
                rows[name]["tail"].append(tmat[:, jm].mean())
    df = pd.DataFrame([dict(method=n_,
                            grouped_loss=float(np.mean(rows[n_]["grp"])),
                            grouped_std=float(np.std(rows[n_]["grp"])),
                            tail_loss=float(np.mean(rows[n_]["tail"])))
                       for n_ in METHOD_ORDER])
    df.to_csv(f"{outdir}/tables/redundancy.csv", index=False)
    big = np.vstack([store_grp[k] for k in store_grp])
    blk, ranks, cd = _stats_block(store_grp)
    with open(f"{outdir}/tables/redundancy_stats.json", "w") as f:
        json.dump(blk, f, indent=2)
    return df, blk


def per_family_table(reps=30, n=300, n_test=400, seed=7, outdir="results",
                     geom="concave", m=8):
    """Out-of-class loss broken down by held-out utility family for one setting."""
    rng_master = np.random.default_rng(seed)
    _fams = ["linear", "chebyshev", "aug_asf", "ces", "choquet", "satisfice"]
    acc = {name: {fam: [] for fam in _fams} for name in METHOD_ORDER}
    for rep in range(reps):
        rng = np.random.default_rng(rng_master.integers(1 << 31))
        F = problems.make_candidate_set(geom, n, m, rng)
        test_seed = int(rng_master.integers(1 << 31))
        sel_rng = np.random.default_rng(int(rng_master.integers(1 << 31)))
        for name in METHOD_ORDER:
            idx = _select(name, F, rng=sel_rng)
            _, per = metrics.out_of_class_loss(
                F, idx, np.random.default_rng(test_seed),
                n_per_family=n_test, by_family=True)
            for fam, v in per.items():
                acc[name][fam].append(v)
    fam_names = ["linear", "chebyshev", "aug_asf", "ces", "choquet", "satisfice"]
    rows = []
    for name in METHOD_ORDER:
        row = dict(method=name)
        for fam in fam_names:
            row[fam] = float(np.mean(acc[name][fam]))
        row["overall"] = float(np.mean([row[f] for f in fam_names]))
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(f"{outdir}/tables/per_family_{geom}_m{m}.csv", index=False)
    return df


def worstcase_table(reps=30, n=300, seed=11, outdir="results", geom="concave", m=8):
    """Worst-case regret + regret uniformity by method (LUR's own certificate)."""
    rng_master = np.random.default_rng(seed)
    acc = {name: {"wcr": [], "ru": []} for name in METHOD_ORDER}
    for rep in range(reps):
        rng = np.random.default_rng(rng_master.integers(1 << 31))
        F = problems.make_candidate_set(geom, n, m, rng)
        sel_rng = np.random.default_rng(int(rng_master.integers(1 << 31)))
        for name in METHOD_ORDER:
            idx = _select(name, F, rng=sel_rng)
            acc[name]["wcr"].append(metrics.worst_case_regret(F, idx))
            acc[name]["ru"].append(metrics.regret_uniformity(F, idx))
    rows = [dict(method=n_,
                 wcr_mean=float(np.mean(acc[n_]["wcr"])),
                 wcr_std=float(np.std(acc[n_]["wcr"])),
                 ru_mean=float(np.mean(acc[n_]["ru"]))) for n_ in METHOD_ORDER]
    df = pd.DataFrame(rows)
    df.to_csv(f"{outdir}/tables/worstcase_{geom}_m{m}.csv", index=False)
    return df


def ablation_table(reps=30, n=300, n_test=400, seed=23, outdir="results",
                   geom="concave", m=8):
    """Ablate LUR probe components; report overall out-of-class loss + WCR."""
    configs = {
        "Full LUR": dict(),
        "No clustering": dict(use_clusters=False),
        "No singletons": dict(use_singletons=False),
        "Mean only": dict(use_max=False),
        "Max only": dict(use_mean=False),
    }
    rng_master = np.random.default_rng(seed)
    acc = {c: {"loss": [], "wcr": []} for c in configs}
    for rep in range(reps):
        rng = np.random.default_rng(rng_master.integers(1 << 31))
        F = problems.make_candidate_set(geom, n, m, rng)
        test_seed = int(rng_master.integers(1 << 31))
        for c, pk in configs.items():
            idx = methods.lur(F, probe_kwargs=pk)
            acc[c]["loss"].append(metrics.out_of_class_loss(
                F, idx, np.random.default_rng(test_seed), n_per_family=n_test))
            acc[c]["wcr"].append(metrics.worst_case_regret(F, idx))
    rows = [dict(config=c, loss_mean=float(np.mean(acc[c]["loss"])),
                 loss_std=float(np.std(acc[c]["loss"])),
                 wcr_mean=float(np.mean(acc[c]["wcr"]))) for c in configs]
    df = pd.DataFrame(rows)
    df.to_csv(f"{outdir}/tables/ablation_{geom}_m{m}.csv", index=False)
    return df


def probe_reduction_table(n=400, seed=3, outdir="results"):
    """Full coalition count (3*2^m - ...) vs. adaptive cluster-probe count."""
    rng = np.random.default_rng(seed)
    rows = []
    for m in [3, 5, 8, 10, 15]:
        F = problems.make_candidate_set("concave", n, m, rng)
        probes, labels = methods.build_probes(F, theta=0.6)
        # full family = {mean_S, max_S : non-empty S subset of {1..m}};
        # mean and max coincide on singletons, so the count is 2(2^m-1)-m.
        full = 2 * (2 ** m - 1) - m
        rows.append(dict(m=m, full_coalitions=full, cluster_probes=len(labels),
                         reduction=round(full / len(labels), 1)))
    df = pd.DataFrame(rows)
    df.to_csv(f"{outdir}/tables/probe_reduction.csv", index=False)
    return df


def sensitivity_theta(reps=20, n=300, n_test=300, seed=31, outdir="results", m=8):
    """theta sensitivity across ALL four geometries (addresses the concern that
    robustness was only shown on one geometry)."""
    thetas = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    fig, ax = plt.subplots(figsize=(5.5, 3.2))
    out = {"theta": thetas}
    for geom in GEOMS:
        rng_master = np.random.default_rng(seed + hash(geom) % 1000)
        means = []
        for th in thetas:
            vals = []
            for rep in range(reps):
                rng = np.random.default_rng(rng_master.integers(1 << 31))
                F = problems.make_candidate_set(geom, n, m, rng)
                test_seed = int(rng_master.integers(1 << 31))
                idx = methods.lur(F, theta=th)
                vals.append(metrics.out_of_class_loss(
                    F, idx, np.random.default_rng(test_seed), n_per_family=n_test))
            means.append(float(np.mean(vals)))
        ax.plot(thetas, means, marker="o", label=geom)
        out[geom] = means
    ax.set_xlabel(r"clustering threshold $\theta$")
    ax.set_ylabel("out-of-class loss"); ax.legend(fontsize=8)
    ax.set_title(f"LUR sensitivity to $\\theta$ across geometries (m={m})", fontsize=9)
    fig.tight_layout(); os.makedirs(f"{outdir}/figures", exist_ok=True)
    fig.savefig(f"{outdir}/figures/sensitivity_theta.pdf"); plt.close(fig)
    pd.DataFrame(out).to_csv(f"{outdir}/tables/sensitivity_theta.csv", index=False)
    return out


def stochastic_demo(reps=40, n=200, m=6, seed=71, outdir="results"):
    """Empirically validate the stochastic extension (Thm 6): as the number of
    observations n_obs grows, the stochastic-LUR winner (using alpha-confidence
    regret on noisy criterion samples) converges to the true (noise-free) LUR
    winner. Reports recovery rate vs n_obs and saves a figure."""
    obs_grid = [1, 2, 5, 10, 20, 50, 100]
    rng_master = np.random.default_rng(seed)
    rec = {k: [] for k in obs_grid}
    for rep in range(reps):
        rng = np.random.default_rng(rng_master.integers(1 << 31))
        Ftrue = problems.make_candidate_set("concave", n, m, rng)
        true_idx = methods.lur(Ftrue)
        noise = 0.15 * (Ftrue.std(axis=0) + 1e-6)
        for nobs in obs_grid:
            hit = 0
            for _ in range(5):
                samples = (Ftrue[None, :, :]
                           + noise[None, None, :] * rng.standard_normal((nobs, n, m)))
                mu = samples.mean(axis=0)
                idx = methods.lur(mu)            # plug-in stochastic-LUR (alpha=0.5)
                hit += int(idx == true_idx)
            rec[nobs].append(hit / 5)
    means = [float(np.mean(rec[k])) for k in obs_grid]
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(obs_grid, means, marker="o")
    ax.set_xscale("log"); ax.set_xlabel("observations per criterion $n$")
    ax.set_ylabel("true-winner recovery rate")
    ax.set_title(f"Stochastic LUR consistency (concave, m={m})", fontsize=9)
    fig.tight_layout(); os.makedirs(f"{outdir}/figures", exist_ok=True)
    fig.savefig(f"{outdir}/figures/stochastic_consistency.pdf"); plt.close(fig)
    df = pd.DataFrame(dict(n_obs=obs_grid, recovery=means))
    df.to_csv(f"{outdir}/tables/stochastic_consistency.csv", index=False)
    return df


def sensitivity_nadir(reps=20, n=300, n_test=300, seed=37, outdir="results",
                      geom="concave", m=8):
    """Inject multiplicative error into the nadir estimate; track loss + how often
    the LUR choice changes vs. the exact-nadir choice."""
    errs = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5]
    rng_master = np.random.default_rng(seed)
    means, flip = [], []
    for e in errs:
        vals, flips = [], []
        for rep in range(reps):
            rng = np.random.default_rng(rng_master.integers(1 << 31))
            F = problems.make_candidate_set(geom, n, m, rng)
            test_seed = int(rng_master.integers(1 << 31))
            ideal = F.min(axis=0); nadir0 = F.max(axis=0)
            idx0 = methods.lur(F, ideal=ideal, nadir=nadir0)
            pert = nadir0 * (1 + e * rng.standard_normal(m))
            pert = np.maximum(pert, ideal + 1e-3)
            idxe = methods.lur(F, ideal=ideal, nadir=pert)
            vals.append(metrics.out_of_class_loss(
                F, idxe, np.random.default_rng(test_seed), n_per_family=n_test))
            flips.append(0.0 if idxe == idx0 else 1.0)
        means.append(np.mean(vals)); flip.append(np.mean(flips))
    fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(errs, means, marker="o", label="out-of-class loss")
    ax.plot(errs, flip, marker="s", label="choice-change rate")
    ax.set_xlabel("relative nadir error (std)"); ax.legend(fontsize=8)
    ax.set_title(f"LUR sensitivity to nadir error ({geom}, m={m})", fontsize=9)
    fig.tight_layout(); fig.savefig(f"{outdir}/figures/sensitivity_nadir.pdf"); plt.close(fig)
    pd.DataFrame(dict(nadir_err=errs, loss=means, flip_rate=flip)).to_csv(
        f"{outdir}/tables/sensitivity_nadir.csv", index=False)
    return errs, means, flip


def agreement_with_smaa(reps=40, n=300, seed=41, outdir="results"):
    """How often does LUR's recommendation coincide with SMAA's, and how far
    apart are they when they differ (objective-space distance)."""
    rng_master = np.random.default_rng(seed)
    rows = []
    for geom in GEOMS:
        for m in MS:
            agree, dists = 0, []
            for rep in range(reps):
                rng = np.random.default_rng(rng_master.integers(1 << 31))
                F = problems.make_candidate_set(geom, n, m, rng)
                i_lur = methods.lur(F)
                i_smaa = methods.smaa(F, rng=np.random.default_rng(99 + rep))
                if i_lur == i_smaa:
                    agree += 1
                r = methods.normalize(F)
                dists.append(float(np.linalg.norm(r[i_lur] - r[i_smaa])))
            rows.append(dict(geometry=geom, m=m,
                             agreement=agree / reps,
                             mean_gap=float(np.mean(dists))))
    df = pd.DataFrame(rows)
    df.to_csv(f"{outdir}/tables/agreement_smaa.csv", index=False)
    return df


def dominated_exclusion_check(trials=200, n=200, seed=5):
    """Empirically verify Corollary 2.1: LUR never selects a dominated point."""
    rng = np.random.default_rng(seed)
    violations = 0
    for _ in range(trials):
        m = int(rng.integers(3, 9))
        geom = GEOMS[int(rng.integers(0, len(GEOMS)))]
        F = problems.make_candidate_set(geom, n, m, rng, n_dominated=30)
        idx = methods.lur(F)
        if metrics.is_dominated(F, idx):
            violations += 1
    return dict(trials=trials, violations=violations)
