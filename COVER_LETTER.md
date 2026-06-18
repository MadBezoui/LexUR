# Cover Letter — EJOR submission

**To:** The Editors, *European Journal of Operational Research* (Decision Support area)
**Re:** Submission of *Beyond Pareto Fronts: A Leximax Universal-Regret Core for Robust Multicriteria Decision Support*

Dear Editors,

We submit the above manuscript for consideration as a full paper in the **Decision Support** area of EJOR.

**New contribution to OR.** The paper introduces the Leximax Universal-Regret (LUR) core, a Pareto-compatible decision rule that replaces the efficient set as the final object of multicriteria analysis with an *auditable regret certificate*. Given only a declared family of monotone "probes" (rational questions over the criteria), LUR returns a single robust recommendation by minimising, lexicographically, the sorted vector of normalised regrets — requiring no ex ante weights, no thresholds, and no pre-generated front. We prove existence and completeness, Pareto compatibility, dominated-solution exclusion, stability under bounded perturbations, and a probe-approximation bound, and we give a redundancy-aware probe construction that keeps the family linear in the number of criteria.

**Fit to the Decision Support area.** The work is squarely in robust multicriteria decision analysis. We position LUR explicitly against the closest literature — stochastic multicriteria acceptability analysis (SMAA), robust ordinal regression, and preference robust optimisation — and show both how it differs (object, criterion, and interpretable output) and that it *generalises* achievement scalarisation, the weighted sum, and lexicographic maximin as special cases of the probe family.

**Headline results.** In a replicated held-out study (four front geometries, m ∈ {3,5,8,10}, 30 replications, 480 instances) and a six-objective stochastic smart-grid dispatch case, evaluated against six preference families — additive *and* non-additive (Choquet, satisficing) — not used during selection: (i) LUR attains best-group worst-case (tail) held-out loss — practically equivalent to the strongest robust scalarisations (negligible effect size) and 11–47% better than the distance-based and Monte-Carlo preference methods used in practice (TOPSIS, knee, SMAA, random weights); (ii) it reduces sensitivity to redundant criteria via correlation clustering; and (iii) it certifies its recommendation and extends natively to noisy criteria and multiple stakeholders. We are explicit about scope: LUR relocates preference modelling into a declared probe family rather than removing it, and does not dominate the strongest robust scalarisations on average-case loss. All comparisons use Friedman/Nemenyi and Holm-corrected Wilcoxon tests with effect sizes.

**Reproducibility.** A complete, anonymised code and data package regenerates every table and figure in the paper with a single command; it is referenced in the manuscript and available to reviewers.

**Originality and ethics.** The manuscript is original, is not under consideration elsewhere, and has not been published previously. All authors approve the submission and declare no conflicts of interest. The manuscript is within the journal's 30-page limit.

We suggest, as potential reviewers, researchers active in robust MCDA and preference modelling whose work we engage in the paper (the SMAA, robust ordinal regression, and preference-robust-optimisation communities). We thank you for considering our work.

Sincerely,

[Author Names], on behalf of all authors
[Affiliation] · [Email]
