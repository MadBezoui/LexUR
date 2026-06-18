"""Selection methods operating on a finite candidate set.

Every method takes an (N x m) objective matrix `F` (minimisation) and returns
the *index* of the recommended candidate.  All methods operate on the normalised
matrix r in [0,1]^m unless noted.

Implemented:
    Classical post-processing : topsis, compromise_programming, knee_point,
                                random_weights, asf
    Robust MCDA               : smaa, minimax_regret   (Savage regret over a
                                linear weight set)
    Proposed                  : lur  (Leximax Universal-Regret core, with
                                adaptive correlation-clustering probes)
"""
from __future__ import annotations
import numpy as np

EPS = 1e-9


# --------------------------------------------------------------------------- #
# normalisation
# --------------------------------------------------------------------------- #
def normalize(F: np.ndarray, ideal: np.ndarray | None = None,
              nadir: np.ndarray | None = None) -> np.ndarray:
    if ideal is None:
        ideal = F.min(axis=0)
    if nadir is None:
        nadir = F.max(axis=0)
    return (F - ideal) / np.maximum(nadir - ideal, EPS)


# --------------------------------------------------------------------------- #
# classical post-processing methods
# --------------------------------------------------------------------------- #
def topsis(F, w=None, **kw):
    r = normalize(F)
    m = r.shape[1]
    w = np.ones(m) / m if w is None else np.asarray(w)
    v = r * w
    d_best = np.linalg.norm(v - v.min(axis=0), axis=1)   # to ideal (0)
    d_worst = np.linalg.norm(v - v.max(axis=0), axis=1)  # to nadir (1)
    closeness = d_worst / (d_best + d_worst + EPS)
    return int(np.argmax(closeness))


def compromise_programming(F, w=None, p=2, **kw):
    r = normalize(F)
    m = r.shape[1]
    w = np.ones(m) / m if w is None else np.asarray(w)
    dist = (np.sum(w * r ** p, axis=1)) ** (1.0 / p)     # L_p to ideal (0)
    return int(np.argmin(dist))


def knee_point(F, **kw):
    """Distance-to-hyperplane knee: plane through the m extreme points
    (best-in-one-objective); pick the candidate farthest below it (toward ideal)."""
    r = normalize(F)
    m = r.shape[1]
    extremes = np.array([r[np.argmax(r[:, i])] for i in range(m)])
    try:
        a = np.linalg.solve(extremes, np.ones(m))        # plane a^T r = 1
        dist = 1.0 - r @ a                               # >0 below the plane
        return int(np.argmax(dist))
    except np.linalg.LinAlgError:
        return compromise_programming(F)


def random_weights(F, n_weights=200, rng=None, **kw):
    """Pick the candidate most frequently optimal across random linear weights
    (a simple robustness-by-popularity baseline)."""
    rng = np.random.default_rng(0) if rng is None else rng
    r = normalize(F)
    m = r.shape[1]
    W = rng.dirichlet(np.ones(m), size=n_weights)
    winners = np.argmin(r @ W.T, axis=0)                 # best per weight
    counts = np.bincount(winners, minlength=r.shape[0])
    return int(np.argmax(counts))


def asf(F, w=None, rho=1e-4, **kw):
    """Augmented achievement scalarising function, reference point = ideal."""
    r = normalize(F)
    m = r.shape[1]
    w = np.ones(m) / m if w is None else np.asarray(w)
    val = np.max(r / (w + EPS), axis=1) + rho * np.sum(r, axis=1)
    return int(np.argmin(val))


def vikor(F, w=None, v=0.5, **kw):
    """VIKOR compromise ranking; recommend the top-ranked Q alternative."""
    r = normalize(F)
    m = r.shape[1]
    w = np.ones(m) / m if w is None else np.asarray(w)
    S = (w * r).sum(axis=1)                       # group utility (already 0..)
    R = (w * r).max(axis=1)                       # individual regret
    Sm, SM = S.min(), S.max(); Rm, RM = R.min(), R.max()
    Q = v * (S - Sm) / (SM - Sm + EPS) + (1 - v) * (R - Rm) / (RM - Rm + EPS)
    return int(np.argmin(Q))


def hypervolume_pick(F, **kw):
    """Pick the alternative with the largest dominated-hypervolume contribution
    to the reference (nadir) point, approximated by the product of slacks."""
    r = normalize(F)
    contrib = np.prod(np.maximum(1.0 - r, 0.0), axis=1)   # box to nadir=1
    return int(np.argmax(contrib))


def dist_to_ideal(F, **kw):
    r = normalize(F)
    return int(np.argmin(np.linalg.norm(r, axis=1)))


def chebyshev_mmr(F, n_weights=1000, rng=None, **kw):
    """Minimax regret under weighted-Chebyshev utilities over a weight set."""
    rng = np.random.default_rng(0) if rng is None else rng
    r = normalize(F); n, m = r.shape
    W = rng.dirichlet(np.ones(m), size=n_weights)
    C = np.stack([np.max(W[t] * r, axis=1) for t in range(n_weights)], axis=1)  # NxT
    regret = C - C.min(axis=0, keepdims=True)
    return int(np.argmin(regret.max(axis=1)))


# --------------------------------------------------------------------------- #
# robust-MCDA baselines
# --------------------------------------------------------------------------- #
def smaa(F, n_weights=1000, rng=None, **kw):
    """SMAA-2 style: Monte-Carlo over the uniform weight simplex with additive
    (linear) value; recommend the alternative with the highest first-rank
    acceptability index (ties broken by expected value)."""
    rng = np.random.default_rng(0) if rng is None else rng
    r = normalize(F)
    n, m = r.shape
    W = rng.dirichlet(np.ones(m), size=n_weights)
    V = -(r @ W.T)                                        # value, higher better
    first = np.argmax(V, axis=0)
    a1 = np.bincount(first, minlength=n) / n_weights     # rank-1 acceptability
    exp_val = V.mean(axis=1)
    order = np.lexsort((exp_val, a1))                     # primary a1, tie exp_val
    return int(order[-1])


def minimax_regret(F, n_weights=1000, rng=None, **kw):
    """Savage minimax regret over a linear weight set: choose the alternative
    minimising its maximum (over weights) regret vs. the best alternative."""
    rng = np.random.default_rng(0) if rng is None else rng
    r = normalize(F)
    n, m = r.shape
    W = rng.dirichlet(np.ones(m), size=n_weights)
    C = r @ W.T                                           # cost (lower better)
    best = C.min(axis=0, keepdims=True)
    regret = C - best                                    # >=0
    max_regret = regret.max(axis=1)
    return int(np.argmin(max_regret))


# --------------------------------------------------------------------------- #
# LUR — Leximax Universal-Regret core
# --------------------------------------------------------------------------- #
def correlation_clusters(F: np.ndarray, theta: float = 0.6) -> list[list[int]]:
    """Group *redundant* objectives, i.e. those with strong POSITIVE Pearson
    correlation (>= theta), via single-linkage connected components.

    Redundancy is positive correlation: two objectives that rise and fall
    together carry duplicate information.  Negatively correlated objectives are
    genuine trade-offs and must stay separate, so we threshold the signed
    correlation, not its absolute value."""
    m = F.shape[1]
    C = np.corrcoef(F.T)
    C = np.nan_to_num(C, nan=0.0)
    adj = C >= theta
    seen = np.zeros(m, dtype=bool)
    clusters = []
    for i in range(m):
        if seen[i]:
            continue
        stack, comp = [i], []
        while stack:
            u = stack.pop()
            if seen[u]:
                continue
            seen[u] = True
            comp.append(u)
            stack.extend(int(v) for v in np.where(adj[u])[0] if not seen[v])
        clusters.append(sorted(comp))
    return clusters


def build_probes(F, theta=0.6, use_singletons=True, use_mean=True,
                 use_max=True, use_clusters=True):
    """Return a list of probe callables q(r)->(N,) and their labels.

    The probe family always anchors three canonical "rational questions":
      * singleton probes  f_i            (each criterion on its own),
      * the grand-mean probe  mean(all)  (the utilitarian compromise question),
      * the grand-max probe   max(all)   (the egalitarian worst-criterion question).
    When objectives are redundant (positively correlated), correlation
    clustering adds one mean and one max probe per cluster, so a redundant group
    is asked about *once* rather than once per member -- this is what protects
    LUR from the redundancy bias that distorts averaging methods, while keeping
    the probe count linear in m and the number of clusters.

    All probes are monotone non-decreasing in each r_i (nonneg weights / max),
    guaranteeing Pareto compatibility (Thm 2/4)."""
    m = F.shape[1]
    probes, labels = [], []
    if use_singletons:
        for i in range(m):
            probes.append(lambda r, i=i: r[:, i])
            labels.append(f"f{i+1}")
    if m > 1:                                   # canonical anchors
        if use_mean:
            probes.append(lambda r: r.mean(axis=1)); labels.append("mean(all)")
        if use_max:
            probes.append(lambda r: r.max(axis=1)); labels.append("max(all)")
    clusters = correlation_clusters(F, theta) if use_clusters else []
    for c in clusters:
        if len(c) < 2:
            continue                            # singleton clusters add nothing new
        idx = np.array(c)
        if use_mean:
            probes.append(lambda r, idx=idx: r[:, idx].mean(axis=1))
            labels.append("mean(" + ",".join(f"f{i+1}" for i in c) + ")")
        if use_max:
            probes.append(lambda r, idx=idx: r[:, idx].max(axis=1))
            labels.append("max(" + ",".join(f"f{i+1}" for i in c) + ")")
    return probes, labels


def disappointment_matrix(F, probes, ideal=None, nadir=None):
    """Return D (N x K): normalised disappointment of each candidate per probe."""
    r = normalize(F, ideal, nadir)
    cols = []
    for q in probes:
        v = q(r)
        qstar, qminus = v.min(), v.max()
        cols.append((v - qstar) / (qminus - qstar + EPS))
    return np.column_stack(cols)


def leximax_argmin(D: np.ndarray, tol: float = 1e-9) -> int:
    """Index minimising the lexicographically-sorted (descending) regret vector."""
    sorted_desc = -np.sort(-D, axis=1)
    sorted_desc = np.round(sorted_desc / tol) * tol      # tolerance for ties
    # lexicographic argmin over rows
    best = 0
    for i in range(1, sorted_desc.shape[0]):
        a, b = sorted_desc[i], sorted_desc[best]
        cmp = np.where(a != b)[0]
        if cmp.size and a[cmp[0]] < b[cmp[0]]:
            best = i
    return int(best)


def lur(F, theta=0.6, ideal=None, nadir=None, return_detail=False,
        probe_kwargs=None, **kw):
    probe_kwargs = probe_kwargs or {}
    probes, labels = build_probes(F, theta=theta, **probe_kwargs)
    D = disappointment_matrix(F, probes, ideal, nadir)
    idx = leximax_argmin(D)
    if return_detail:
        return idx, D, labels, probes
    return idx


def build_full_probes(F):
    """Full coalition family {mean_S, max_S : non-empty S}; for small m only."""
    import itertools
    m = F.shape[1]
    probes, labels = [], []
    for k in range(1, m + 1):
        for S in itertools.combinations(range(m), k):
            idx = np.array(S)
            probes.append(lambda r, idx=idx: r[:, idx].mean(axis=1))
            labels.append("mean" + str(S))
            if k > 1:
                probes.append(lambda r, idx=idx: r[:, idx].max(axis=1))
                labels.append("max" + str(S))
    return probes, labels


def build_random_probes(F, k, rng):
    """k random monotone (nonneg-weight) linear probes -- a control with the same
    probe budget as the adaptive family but no structure."""
    m = F.shape[1]
    probes, labels = [], []
    for j in range(k):
        w = rng.dirichlet(np.ones(m))
        probes.append(lambda r, w=w: r @ w)
        labels.append(f"rand{j}")
    return probes, labels


def lur_variant(F, variant="adaptive", rng=None, theta=0.6, return_detail=False, **kw):
    """LUR probe-design controls used in the ablation/probe study."""
    rng = np.random.default_rng(0) if rng is None else rng
    if variant == "adaptive":
        probes, labels = build_probes(F, theta=theta)
    elif variant == "full":
        probes, labels = build_full_probes(F)
    elif variant == "singletons":
        probes, labels = build_probes(F, use_mean=False, use_max=False, use_clusters=False)
    elif variant == "no_singletons":
        probes, labels = build_probes(F, use_singletons=False)
    elif variant == "max_only":
        probes, labels = build_probes(F, use_mean=False)
    elif variant == "cluster_only":
        probes, labels = build_probes(F, use_singletons=False, use_mean=True, use_max=True)
    elif variant == "random":
        k = len(build_probes(F, theta=theta)[1])
        probes, labels = build_random_probes(F, k, rng)
    else:
        raise ValueError(variant)
    
    D = disappointment_matrix(F, probes)
    idx = leximax_argmin(D)
    if return_detail:
        return idx, D, labels, probes
    return idx


# --------------------------------------------------------------------------- #
# registry
# --------------------------------------------------------------------------- #
METHODS = {
    "TOPSIS": topsis,
    "CP": compromise_programming,
    "VIKOR": vikor,
    "Knee": knee_point,
    "HV": hypervolume_pick,
    "DistIdeal": dist_to_ideal,
    "RW": random_weights,
    "ASF": asf,
    "SMAA": smaa,
    "MMR": minimax_regret,
    "ChebMMR": chebyshev_mmr,
    "LUR": lur,
}
CLASSICAL = ["TOPSIS", "CP", "VIKOR", "Knee", "HV", "DistIdeal", "RW", "ASF"]
ROBUST = ["SMAA", "MMR", "ChebMMR"]
RANDOMIZED = {"RW", "SMAA", "MMR", "ChebMMR"}    # need an rng
