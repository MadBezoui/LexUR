"""Non-parametric statistical comparison utilities.

    friedman            : Friedman chi-square test across methods
    nemenyi_cd          : critical difference for the Nemenyi post-hoc test
    average_ranks       : mean ranks (lower loss -> better rank)
    wilcoxon_holm       : pairwise Wilcoxon signed-rank vs. a control, Holm-corrected
    cliffs_delta        : non-parametric effect size
"""
from __future__ import annotations
import numpy as np
from scipy import stats

# Studentised range / sqrt(2) constants q_alpha for Nemenyi at alpha=0.05
# indexed by number of methods k (2..12). Source: Demsar (2006), Table 5.
_Q05 = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949,
        8: 3.031, 9: 3.102, 10: 3.164, 11: 3.219, 12: 3.268}


def average_ranks(loss_matrix: np.ndarray) -> np.ndarray:
    """loss_matrix: (n_datasets x k_methods), lower is better.
    Returns mean rank per method (1 = best)."""
    ranks = np.apply_along_axis(stats.rankdata, 1, loss_matrix)
    return ranks.mean(axis=0)


def friedman(loss_matrix: np.ndarray):
    stat, p = stats.friedmanchisquare(*[loss_matrix[:, j]
                                        for j in range(loss_matrix.shape[1])])
    return float(stat), float(p)


def nemenyi_cd(k: int, n: int, alpha: float = 0.05) -> float:
    q = _Q05.get(k)
    if q is None:
        raise ValueError(f"no tabulated q for k={k}")
    return float(q * np.sqrt(k * (k + 1) / (6.0 * n)))


def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """delta in [-1,1]; >0 means a tends to be LARGER than b."""
    a, b = np.asarray(a), np.asarray(b)
    gt = sum((a[:, None] > b[None, :]).sum(axis=1))
    lt = sum((a[:, None] < b[None, :]).sum(axis=1))
    return float((gt - lt) / (len(a) * len(b)))


def wilcoxon_holm(loss_matrix: np.ndarray, names, control: str):
    """Pairwise Wilcoxon signed-rank of `control` vs. every other method,
    Holm-Bonferroni corrected.  Returns dict name -> (p_raw, p_holm, delta)."""
    j_ctrl = names.index(control)
    others = [j for j in range(len(names)) if j != j_ctrl]
    raw = {}
    for j in others:
        x, y = loss_matrix[:, j_ctrl], loss_matrix[:, j]
        try:
            _, p = stats.wilcoxon(x, y)
        except ValueError:
            p = 1.0
        raw[names[j]] = (p, cliffs_delta(y, x))   # delta>0: other worse than control
    # Holm correction
    ordered = sorted(raw.items(), key=lambda kv: kv[1][0])
    out, k = {}, len(ordered)
    for rank, (nm, (p, d)) in enumerate(ordered):
        p_holm = min(1.0, p * (k - rank))
        out[nm] = (p, p_holm, d)
    return out
