"""Acceptance gates and paired statistics for the EJOR validation protocol.

Gates (each returns a dict with a boolean `pass` and the supporting numbers):
    gate_dominated_injection : LUR never selects a dominated alternative.
    gate_affine_invariance   : LUR choice is invariant to positive affine rescaling.
    gate_nadir_error         : quality stable / choice-change reported under nadir error.
    noninferiority           : paired non-inferiority of LUR vs a control on tail loss.
"""
from __future__ import annotations
import numpy as np
from scipy import stats as sps
from . import problems, methods, families
from .methods import normalize


# --------------------------------------------------------------------------- #
def gate_dominated_injection(ratios, trials=150, n=200, seed=5):
    """Inject dominated alternatives at several ratios; LUR must never pick one,
    and we also report how often the chosen non-dominated solution changes when
    bounds are recomputed after injection."""
    rng = np.random.default_rng(seed)
    geoms = problems.GEOMETRIES
    violations = 0
    change = {r: 0 for r in ratios}
    total = 0
    for _ in range(trials):
        m = int(rng.integers(3, 9))
        g = geoms[int(rng.integers(0, len(geoms)))]
        F0 = problems.make_candidate_set(g, n, m, rng)
        base_idx = methods.lur(F0)
        base_choice = F0[base_idx].copy()
        total += 1
        for r in ratios:
            k = int(r * n)
            if k == 0:
                continue
            anchors = F0[rng.integers(0, F0.shape[0], size=k)]
            dom = anchors + rng.uniform(0.05, 0.4, size=anchors.shape)  # strictly worse
            F = np.vstack([F0, dom])
            idx = methods.lur(F)
            # dominated-selection check
            f = F[idx]
            dommask = np.all(F <= f, axis=1) & np.any(F < f, axis=1)
            dommask[idx] = False
            if dommask.any():
                violations += 1
            # choice-change among non-dominated (bounds recomputed on F)
            if not np.allclose(F[idx], base_choice):
                change[r] += 1
    return dict(name="dominated_injection",
                violations=int(violations), trials=int(total),
                **{f"change_rate_{r}": round(change[r] / total, 3) for r in ratios if r > 0},
                **{"pass": violations == 0})


def gate_affine_invariance(tests=3000, n=150, seed=9, tol=0):
    """Random positive affine rescaling f_i' = a_i f_i + b_i (a_i>0). With bounds
    recomputed consistently, LUR must select the SAME alternative."""
    rng = np.random.default_rng(seed)
    geoms = problems.GEOMETRIES
    same = 0
    for _ in range(tests):
        m = int(rng.integers(3, 9))
        g = geoms[int(rng.integers(0, len(geoms)))]
        F = problems.make_candidate_set(g, n, m, rng)
        i0 = methods.lur(F)
        a = rng.uniform(0.2, 5.0, size=m)
        b = rng.uniform(-2.0, 2.0, size=m)
        i1 = methods.lur(F * a + b)
        same += int(i0 == i1)
    rate = same / tests
    return dict(name="affine_invariance", identical_rate=round(rate, 4),
                tests=int(tests), **{"pass": rate >= 0.999})


def gate_nadir_error(errors, reps=30, n=250, m=8, seed=37, n_test=300):
    """Quality (held-out loss) and choice-change vs relative nadir error."""
    rng = np.random.default_rng(seed)
    out = {}
    for e in errors:
        losses, flips = [], []
        for _ in range(reps):
            g = problems.GEOMETRIES[int(rng.integers(0, 4))]
            F = problems.make_candidate_set(g, n, m, rng)
            ideal = F.min(0); nad0 = F.max(0)
            i0 = methods.lur(F, ideal=ideal, nadir=nad0)
            pert = np.maximum(nad0 * (1 + e * rng.standard_normal(m)), ideal + 1e-3)
            ie = methods.lur(F, ideal=ideal, nadir=pert)
            cache = families.loss_cache(F, normalize, np.random.default_rng(1),
                                        n_per_family=n_test)
            losses.append(families.losses_from(cache, ie)[1])     # tail
            flips.append(float(ie != i0))
        out[e] = (float(np.mean(losses)), float(np.mean(flips)))
    base = out[errors[0]][0]
    worst = max(v[0] for v in out.values())
    return dict(name="nadir_error",
                loss_by_error={str(e): round(v[0], 4) for e, v in out.items()},
                flip_by_error={str(e): round(v[1], 3) for e, v in out.items()},
                max_quality_degradation=round(worst - base, 4),
                **{"pass": (worst - base) <= 0.05})


# --------------------------------------------------------------------------- #
# paired statistics
# --------------------------------------------------------------------------- #
def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    gt = (a[:, None] > b[None, :]).sum()
    lt = (a[:, None] < b[None, :]).sum()
    return float((gt - lt) / (len(a) * len(b)))


def bootstrap_ci(diff, B=5000, seed=0):
    rng = np.random.default_rng(seed)
    n = len(diff)
    means = [diff[rng.integers(0, n, n)].mean() for _ in range(B)]
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def noninferiority(lur_loss, ctrl_loss, margin=0.01, margin_rel=0.02, name="ctrl"):
    """Paired non-inferiority of LUR vs control on (tail) loss. Per the
    pre-registered protocol the margin is `0.01 normalized OR 2% relative`; we
    report both and declare non-inferiority if EITHER holds (upper 95% bootstrap
    bound of mean(LUR-ctrl) below the margin)."""
    lur_loss = np.asarray(lur_loss); ctrl_loss = np.asarray(ctrl_loss)
    diff = lur_loss - ctrl_loss
    lo, hi = bootstrap_ci(diff)
    try:
        _, p = sps.wilcoxon(lur_loss, ctrl_loss)
    except ValueError:
        p = 1.0
    rel_margin = margin_rel * float(ctrl_loss.mean())
    eff_margin = max(margin, rel_margin)
    return dict(control=name, mean_diff=round(float(diff.mean()), 4),
                ci95=[round(lo, 4), round(hi, 4)], wilcoxon_p=float(p),
                delta=round(cliffs_delta(lur_loss, ctrl_loss), 3),
                margin_abs=margin, margin_rel2pct=round(rel_margin, 4),
                noninferior_abs=bool(hi < margin),
                noninferior=bool(hi < eff_margin))
