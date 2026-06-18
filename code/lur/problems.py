"""Candidate-set generators with controlled Pareto-front geometries.

A *candidate set* A is an (N x m) matrix of objective vectors (minimisation).
We sample finite non-dominated approximations of canonical Pareto-front
geometries (linear / concave / convex / disconnected), mirroring the output of
an a-posteriori multi-objective optimiser.  This is the realistic setting for a
*selection* method: every candidate is (near-)efficient and the task is to pick
a single robust recommendation.

Geometries follow the families used by the DTLZ test suite:
    linear        -> DTLZ1   (front on the simplex  sum f_i = 0.5)
    concave       -> DTLZ2/3/4 (front on the unit sphere  sum f_i^2 = 1)
    convex        -> front  sum sqrt(f_i) = 1
    disconnected  -> DTLZ7-like (several concave patches)
"""
from __future__ import annotations
import numpy as np

GEOMETRIES = ("linear", "concave", "convex", "disconnected")


def _dirichlet_simplex(n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """n points on the (m-1)-simplex, sum_i s_i = 1, s_i >= 0."""
    return rng.dirichlet(np.ones(m), size=n)


def sample_front(geometry: str, n: int, m: int, rng: np.random.Generator) -> np.ndarray:
    """Return an (n x m) non-dominated candidate set for the given geometry."""
    s = _dirichlet_simplex(n, m, rng)
    if geometry == "linear":
        F = 0.5 * s                               # sum f_i = 0.5
    elif geometry == "concave":
        d = rng.random((n, m)) ** 0.5             # spread away from axes
        F = d / np.linalg.norm(d, axis=1, keepdims=True)   # sum f_i^2 = 1
    elif geometry == "convex":
        F = s ** 2                                # sum sqrt(f_i) = 1
    elif geometry == "disconnected":
        # union of a few concave patches with offsets along objective 1
        d = rng.random((n, m)) ** 0.5
        F = d / np.linalg.norm(d, axis=1, keepdims=True)
        patch = rng.integers(0, 4, size=n)
        F[:, 0] = F[:, 0] + 0.6 * patch           # creates gaps -> disconnected
    elif geometry == "asymmetric":
        # concave sphere with heterogeneous criterion scales
        d = rng.random((n, m)) ** 0.5
        F = d / np.linalg.norm(d, axis=1, keepdims=True)
        scales = np.linspace(1.0, 5.0, m)
        F = F * scales
    elif geometry == "manyknee":
        # concave base warped to create multiple knees
        d = rng.random((n, m)) ** 0.5
        F = d / np.linalg.norm(d, axis=1, keepdims=True)
        F = F + 0.15 * np.sin(6.0 * F)
        F = np.clip(F, 0, None)
    elif geometry == "degenerate":
        # lower-dimensional front: last criterion tied to the first
        F = s ** 2
        F[:, -1] = F[:, 0]
    elif geometry == "irregular":
        # concave front with multiplicative noise (noisy/irregular surface)
        d = rng.random((n, m)) ** 0.5
        F = d / np.linalg.norm(d, axis=1, keepdims=True)
        F = F * (1.0 + 0.1 * rng.standard_normal((n, m)))
        F = np.clip(F, 1e-3, None)
    else:
        raise ValueError(f"unknown geometry {geometry!r}")
    return non_dominated(F)


def non_dominated(F: np.ndarray) -> np.ndarray:
    """Return the non-dominated subset of F (minimisation). Vectorised:
    point i is dominated iff some j satisfies F[j] <= F[i] (all) and F[j] < F[i]
    (some). For large N we tile to bound peak memory."""
    n = F.shape[0]
    keep = np.ones(n, dtype=bool)
    block = 256
    for s in range(0, n, block):
        e = min(s + block, n)
        le = (F[None, :, :] <= F[s:e, None, :]).all(axis=2)   # (b x n) F[j]<=F[i]
        lt = (F[None, :, :] < F[s:e, None, :]).any(axis=2)    # (b x n) F[j]<F[i]
        dom = le & lt                                          # j dominates i
        for k in range(e - s):
            dom[k, s + k] = False
        keep[s:e] = ~dom.any(axis=1)
    return F[keep]


def make_redundant_set(geometry: str, n: int, group_sizes, rng: np.random.Generator,
                       noise: float = 0.05):
    """Realistic case motivating correlation clustering: the decision-maker has
    `c = len(group_sizes)` TRUE underlying criteria, but each is measured by
    several redundant (positively correlated) objectives.

    Returns (F, groups) where F is (n x m), m = sum(group_sizes), and groups is a
    length-m array mapping each objective to its underlying criterion index.
    Within a group, objectives are noisy monotone copies of the same criterion,
    so they are strongly positively correlated; across groups they trade off."""
    c = len(group_sizes)
    base = sample_front(geometry, max(2 * n, 64), c, rng)
    base = non_dominated(base)
    while base.shape[0] < n:
        extra = non_dominated(sample_front(geometry, 2 * n, c, rng))
        base = np.vstack([base, extra])
    base = base[:n]
    cols, groups = [], []
    for g, sz in enumerate(group_sizes):
        for _ in range(sz):
            scale = rng.uniform(0.8, 1.2)
            shift = rng.uniform(-0.02, 0.02)
            col = scale * base[:, g] + shift + noise * rng.standard_normal(n)
            cols.append(col)
            groups.append(g)
    F = np.column_stack(cols)
    F = F - F.min(axis=0) + 1e-3                 # keep positive
    return F, np.array(groups), base


def make_candidate_set(geometry: str, n: int, m: int, rng: np.random.Generator,
                       n_dominated: int = 0) -> np.ndarray:
    """Build a candidate set of >= n non-dominated points (resampling until met),
    optionally appended with `n_dominated` strictly dominated interior points
    (used to test dominated-exclusion)."""
    # Single oversample + single non-dominated pass (bounded cost ~O((1.5n)^2 m)).
    # sample_front already returns points on the front, so this yields ~n
    # non-dominated points for typical geometries; for low-fraction geometries
    # (e.g. degenerate at small m) it returns somewhat fewer, which is an
    # acceptable candidate set and avoids unbounded resampling.
    raw = sample_front(geometry, int(1.5 * n) + 16, m, rng)
    F = non_dominated(raw)[:n]
    if F.shape[0] < max(8, n // 5):                # safety: ensure enough points
        F = raw[:max(8, n // 5)]
    if n_dominated > 0:
        # interior points dominated by a random anchor in F
        anchors = F[rng.integers(0, F.shape[0], size=n_dominated)]
        dom = anchors + rng.uniform(0.05, 0.25, size=anchors.shape)
        F = np.vstack([F, dom])
    return F
