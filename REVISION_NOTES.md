# Consolidated Reviewer Remarks & Dispositions

Three independent EJOR-style reviews (all: **Major Revision**) were consolidated.
Only the correct, pertinent remarks are kept below, deduplicated, each with the
concrete change made in the manuscript (`paper/`) and/or code (`code/`). Items not
fully resolvable now are marked **Deferred** with justification.

## A. Theory (correctness — highest priority)

1. **Pareto-compatibility (Thm 2) strict part false without separation.** *(all three)*
   Fixed. Split into **weak** (monotonicity only) and **strict** (requires a
   *separating* family; singletons suffice). Added Definition of "separating
   family", a counterexample in-text, and corrected the dominated-exclusion
   corollary to require separation. LUR always includes singletons, so it
   separates. (§3, Appendix A.)

2. **Stability theorem (Thm 3) false under exact lexicographic comparison.** *(R1, R3)*
   Fixed. Restated for the **tolerance-based (τ) leximax** rule actually used in
   the code; new margin condition with proof; explicit note that exact comparison
   (τ=0) is not perturbation-stable. (§3, Appendix A.)

3. **Probe-approximation theorem (Thm 5) too strong / hides ε.** *(all three)*
   Fixed. Demoted to a **perturbation lemma** with the explicit constant `3η/β`
   (β = range floor, worst case ε), stated as a sensitivity result, with an
   explicit disclaimer that it is **not** a ranking/winner guarantee and that
   clustering is not proven to admit η-close approximants. (§5, Appendix A.)

4. **Stochastic theorem (Thm 6) under-specified (nonlinear/max probes, correlations,
   normalization, tie instability).** *(R1, R3)*
   Fixed. Reframed as a **plug-in consistency proposition** under the tolerance
   rule; states that μ_q, σ_q for nonlinear probes are estimated by Monte-Carlo
   from joint samples (not marginal moments) and that anchors use estimated means.
   Added an **empirical validation** (new experiment, §7.7).

## B. Overclaims & factual inconsistencies (correctness)

5. **"No weights / no thresholds / parameter-free" overstated.** *(all three)*
   Fixed. Reframed throughout (abstract, §1, §2, Table 1 caption) as "relocates
   preference modelling into a declared probe family rather than removing it."
   Table 1 caption now clarifies θ is a clustering (not preference) threshold and
   "no front" applies to the direct formulation only.

6. **"Generalises weighted sum/ASF/leximin" overclaimed.** *(all three)*
   Fixed. Now "**recovers** as special cases when reduced to the single
   corresponding probe"; explicitly not a subsumption claim for the full family.

7. **Redundancy "never misled / asked once per member" overclaimed (singletons remain).** *(all three)*
   Fixed. Now "reduces, does not eliminate, redundancy sensitivity"; singletons
   remain (needed for separation) and can affect tie-breaking; the claim is
   empirical, not a duplication-invariance theorem. (abstract, §1, §5.)

8. **Abstract "25–55%" not supported by tables.** *(R1, R3)*
   Fixed. Recomputed from data: tail-loss reduction is **11–47%** vs
   distance/Monte-Carlo methods; abstract and §7 corrected accordingly.

9. **"Flattest profile" claim contradicted by Table 4 (CP is flatter).** *(R1)*
   Fixed. Claim **removed**; replaced with an honest statement that LUR sits
   between the averaging and worst-case camps and is robust across additive *and*
   non-additive families (CP is flatter and has lower mean on that setting).

10. **Nemenyi grouping inconsistent (3.54−2.92 = 0.62 > CD 0.48).** *(R1)*
    Fixed. Recomputed and restated rigorously: LUR is statistically tied with CP
    and very slightly behind MMR/ASF (gaps just beyond CD) but at **negligible
    effect size** (|δ| ≤ 0.034); significantly better than TOPSIS/knee/RW/SMAA.

11. **Promotional tone.** *(R1, R3)* Softened "uniquely", "never misled",
    "least-fragile", "information no scalar score conveys", etc.

## C. Computation (§4)

12. **Direct computation underdeveloped; q\*/q⁻ cost; M-surrogate not exact for
    continuous; OWA constraints; "front-free" not demonstrated.** *(all three)*
    Fixed/tempered. §4 now: LUR is primarily a candidate-set rule (matches the
    experiments); finite case exact; continuous case presented with assumptions;
    added the **cost of the anchors**; added the exact finite-M condition and the
    **cumulative-sum-of-top-p** convex reformulation (Ogryczak); explicit
    statement that large-scale continuous validation is **future work**.

## D. Empirical strengthening

13. **Evaluation may favour additive/probe-like utilities.** *(R2, R3)*
    Fixed. Added **two non-additive held-out families** — a 2-additive **Choquet**
    integral (criterion interactions) and a **satisficing/threshold** utility —
    so six families now span additive and non-additive preferences. All tables
    re-run; LUR remains in the best group on tail loss.

14. **Stochastic extension never evaluated.** *(R2, R3)* Fixed. New experiment
    (§7.7, `stochastic_demo`): true-winner recovery rises 0.04→0.79 as
    observations/criterion grow 1→100.

15. **θ sensitivity shown on one geometry only.** *(R2)* Fixed. θ sweep now run
    across all four geometries (Figure, §7.6).

16. **SMAA comparison apples-to-oranges; define the single-choice rule.** *(R1, R2, R3)*
    Fixed. §2.3 now states SMAA is primarily exploratory and that we use the
    SMAA-2 highest-first-rank-acceptability single-choice device; framed as a
    comparison of decision philosophies.

17. **Baseline parameterization / #held-out samples / MMR weight set unspecified.** *(R1)*
    Fixed. §7.1 now specifies all baseline choices, 300 utilities/family,
    1000 Monte-Carlo weights for SMAA/MMR, θ=0.6, tolerance leximax.

18. **Reproducibility details / repo.** *(all three)* `README.md` documents the
    one-command regeneration; manuscript states code/data release.

## E. Minor (fixed)

- Normalization denominator → `max{z^N−z*, ε}` (paper eq. and `methods.normalize`).
- `q(**0**)=0, q(**1**)=1` clarified as vectors; `q⁻` renamed `q^w` (worst).
- Candidate set vs feasible set: extrema defined over A (finite) vs X (continuous).
- Nadir-over-efficient-set vs worst-over-feasible-set distinction added.
- "Full coalition family" defined precisely as `{mean_S, max_S}` → count
  `2(2^m−1)−m`; Table 2 (probe reduction) recomputed accordingly.
- Re-proofread math; manuscript compiles clean (no undefined refs).

## F. Deferred (with justification)

- **Additional real-world MCDA datasets / expert-validated preferences** *(R2, R3)*:
  not added now; the smart-grid case plus six synthetic geometries and the
  redundancy benchmark are retained, and the limitation is stated explicitly in
  §8 (Threats to validity) as the primary future-work item. Adding curated
  external datasets is the recommended next revision step.
- **Large-scale continuous direct-optimization demonstration** *(R1, R2, R3)*:
  the claim has been tempered to "available in principle"; an empirical
  large-scale continuous study is flagged as future work in §4 and §8.
- **Full axiomatic characterization of the Rawlsian variant** *(R2)*: we continue
  to claim only anonymity/monotonicity/worst-stakeholder protection, not a
  uniqueness/IIA characterization; noted as future work.

## Net effect on claims
The revised paper claims LUR is **in the best-performing group on worst-case loss
(practically equivalent to the strongest robust scalarisations), far better than
the averaging/Monte-Carlo methods used in practice, with an interpretable
certificate, reduced redundancy sensitivity, and native stochastic/fairness
extensions** — and explicitly does **not** claim average-case dominance,
parameter-freedom, redundancy immunity, or a demonstrated large-scale continuous
solver.
