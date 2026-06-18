# Getting "Beyond Pareto Fronts" Accepted at EJOR — Strategic Plan

**Manuscript:** *Beyond Pareto Fronts: A Leximax Universal-Regret (LUR) Core for Multiobjective Optimization*
**Target:** European Journal of Operational Research (EJOR), **Decision Support** area
**Prepared:** 18 June 2026 · Data assumed real & reproducible

---

## 0. Executive summary (read this first)

Good news: **EJOR is the right home for this paper.** Unlike TEVC, there is no scope/reframing problem — preference-free robust selection over conflicting objectives, achievement scalarizing functions, minimax-regret, and lexicographic decision rules are *core* EJOR Decision Support material. You do **not** need to bolt on an evolutionary algorithm. The contribution can stay exactly what it is.

That changes where the risk lives. At EJOR the battle is **novelty positioning against the MCDA / robust-decision literature**, not scope. EJOR desk-rejects anything that lacks "a major new research finding or novel approach to OR," and the Decision Support area is refereed by the people who built the methods you must out-position. The single most dangerous omission in the current draft is that **it does not engage the robust-MCDA literature that is closest to LUR** — above all **SMAA (Stochastic Multicriteria Acceptability Analysis)**, **robust ordinal regression (ROR)**, and **preference robust optimization (PRO)**. Your "evaluate a solution over all rational interpretations of the objectives" idea is conceptually adjacent to SMAA's "evaluate over the feasible weight/preference space." A Decision Support referee will spot this in thirty seconds. Engage it head-on and you have a strong, novel paper; ignore it and you get desk- or first-round rejected.

Realistic read: current draft at EJOR ≈ **likely reject** (novelty not positioned, weak related work, rigor gaps, placeholders, possible over-length). After the positioning + rigor work below ≈ **genuinely competitive** — EJOR is selective (acceptance roughly ~10–16%) but this is squarely in-scope work with a real idea, which is the hard part.

Three things move the needle most, in order:
1. **Position LUR rigorously against SMAA / ROR / PRO / robust MCDA** and prove what it adds.
2. **State the OR contribution and decision-support value explicitly**, with one convincing real decision case.
3. **Bring the empirical and bibliographic rigor to OR-journal standard** and fit ≤30 pages.

---

## 1. Journal-fit assessment (EJOR)

### 1.1 What EJOR is and how it screens

EJOR (Elsevier; the EURO flagship; IF ≈ 6.0; SJR top-quartile in OR/Management Science) publishes original OR papers organized into **areas**; yours belongs to **Decision Support** (the home of MCDA, decision analysis, DEA, preference modelling). Screening is fast and strict:

- The Managing Editor does an **initial technical/English/completeness check**; failures are desk-rejected, usually **within a week**.
- An Editor then judges **OR contribution**: "papers that do not contain a major new research finding or novel approach to the application of OR are likely to be rejected" — and may be rejected for insufficient contribution *even if some reviewers are positive*.
- **Hard length limit: 30 pages** including abstract, figures, tables, references, and appendices (Short Communications: 10). Over-length risks desk rejection. Extra material goes in an **online appendix / e-companion**.
- Poor English alone is grounds for desk rejection.

### 1.2 Why the paper fits — and what that implies

The fit is excellent: LUR is a parameter-light MCDA selection rule with theorems, an algorithm, and a real case study — exactly EJOR's register. The implication is that you compete on **methodological novelty and decision-support insight**, judged by MCDA experts. EJOR cares less than TEVC about massive benchmark horse-races and more about: a clearly articulated new idea, correct theory, honest positioning in the OR literature, a convincing decision-support demonstration, and reproducibility.

---

## 2. Referee-style gap analysis (what EJOR Decision Support reviewers will attack)

Ordered by rejection risk.

### 2.1 Fatal tier (desk- or first-round reject)

1. **Missing the closest literature — robust MCDA.** No engagement with **SMAA** (Lahdelma, Hokkanen & Salminen; Tervonen & Figueira surveys), **robust ordinal regression / GRIP / UTA-family** (Greco, Mousseau, Słowiński; Figueira), or **preference robust optimization** (Armbruster & Delage; Hu & Mehrotra). LUR's "regret over a declared class of monotone probes" is conceptually a *regret-based, robust-MCDA* construct — referees will demand to know precisely how it differs from evaluating over a feasible preference set (SMAA) or a robust utility set (PRO/ROR). **This is the make-or-break issue at EJOR.**
2. **OR contribution not stated as such.** The draft frames the gain as "beyond Pareto fronts," but does not crisply answer "what new, generally useful OR result does this give a decision analyst?" Without an explicit contribution statement an Editor can desk-reject for insufficient contribution.

### 2.2 Major tier (major revision or reject)

3. **Empirical rigor below OR-journal standard.** Tables 2–5 report single numbers with **no replication, dispersion, or significance testing**, and a smart-grid case with stochastic inputs but no reported run counts or confidence intervals. EJOR expects multiple replications, dispersion (std/IQR), and statistical comparison where stochastic.
4. **The "out-of-class regret" metric is ill-defined / self-serving.** `Regret_test(x) = U_test(x) − max_y U_test(y)` is ≤ 0 by construction and the sign/ordering is ambiguous. Reviewers will read this as an evaluation tuned to favor LUR. Redefine it cleanly (non-negative loss vs. best feasible under each held-out utility, lower = better) — and note its kinship to SMAA's acceptability indices, turning a weakness into a positioning strength.
5. **Baselines are classical only.** TOPSIS, compromise programming, knee, ASF, random weights are textbook. Add **robust-MCDA comparators**: an SMAA-based selection, an ROR/UTA-based recommendation, and a robust/regret scalarization. This is what makes the comparison credible *to this audience*.
6. **Thin, dated bibliography.** ~23 refs, mostly textbooks and pre-2010. EJOR expects deep, current MCDA coverage (recent EJOR Decision Support papers especially — referees check that you cite the journal's own relevant work).
7. **Decision-support value under-developed.** The smart-grid case shows numbers but little *managerial/analyst insight*: how does the regret certificate change what a decision-maker actually does? EJOR values a convincing decision narrative, not just metric wins.

### 2.3 Minor tier (reviewers will still list these)

8. Placeholder author/affiliation/correspondence fields.
9. Some theorems are near-trivial (Thm 1 existence, Thm 4 immediate); reframe as lemmas/remarks to avoid a "padded" impression.
10. Theorem 5's proof jumps from a `3η/ε²` bound to `O(Lη)` without justification — tighten.
11. Strong uniqueness-of-claim assertions in Table 1 ("the only method that…") invite a counterexample; soften and cite.
12. Nadir `z^N` estimation sensitivity not studied (a classic MCDA concern reviewers always raise).
13. "Open-source software" asserted but no repository/seed/environment given.
14. Likely **over 30 pages** once formatted in Elsevier style with full proofs — plan the e-companion now.

---

## 3. Strategic acceptance roadmap (sequenced)

Do positioning and rigor before prose; they change what the paper claims.

### Phase 1 — Reposition as robust MCDA (Days 1–3, highest leverage)
- Add the framing: **LUR is a regret-based robust-MCDA recommender** that, instead of integrating over a preference distribution (SMAA) or a robust utility set (ROR/PRO), takes the **lexicographic minimax of normalized regret over a declared class of monotone probes**, and returns an *auditable certificate*.
- Write an explicit **"Contribution to OR"** paragraph in the intro: the new preorder, its certificate, dominated-exclusion + stability guarantees, and direct computability without front enumeration — and *why a decision analyst should care* (no ex ante weights, transparent, auditable, single robust recommendation).
- Add a dedicated related-work subsection: **SMAA, ROR/UTA/GRIP, PRO, robust MCDA, regret theory in MCDA**, ending with a crisp differentiation table (LUR vs. SMAA vs. ROR vs. PRO vs. classical scalarization).

### Phase 2 — Rigor upgrade (Week 1–2)
- Redefine the held-out / out-of-class metric cleanly and connect it to acceptability-index thinking.
- Re-run all experiments with **≥30 replications** where any randomness exists (random weights, stochastic objectives, sampled held-out utilities); report median + IQR (or mean ± std) and **statistical tests** (Wilcoxon / Friedman + post-hoc) with effect sizes.
- Add robust-MCDA baselines (SMAA selection, ROR recommendation, robust/regret scalarization) alongside the classical ones.
- Add **nadir-estimation** and **clustering-threshold θ** sensitivity studies.

### Phase 3 — Decision-support case study (Week 2)
- Turn the smart-grid case into a **narrative decision study**: show the certificate, identify the critical objective coalitions, show how the recommendation and its justification differ from TOPSIS/SMAA, and articulate the managerial takeaway. One deep, well-told case beats many shallow tables for EJOR.

### Phase 4 — Literature & theory cleanup (Week 2–3)
- Expand to ~45–70 references, MCDA- and EJOR-heavy, current (2020–2026). Reframe trivial theorems as lemmas; tighten Thm 5.

### Phase 5 — Manuscript structure, length, reproducibility (Week 3)
- Restructure to Elsevier/EJOR norms (see §5); push long proofs and full tables into an **online appendix** to hold ≤30 pages.
- Public, anonymized **reproducibility repository** (code, data, seeds, scripts regenerating every table/figure); reference it in the paper.

### Phase 6 — Polish, English, mock review (Week 3–4)
- Professional-grade English pass (EJOR desk-rejects on language). Fill author metadata. Get one MCDA-literate colleague to mock-review against §2.

### Phase 7 — Submit
- Elsevier Editorial Manager, **Decision Support** area; cover letter per §6; suggest Decision Support editors/reviewers.

---

## 4. Experiment & reproducibility plan (EJOR-tuned)

EJOR weights *credible positioning + insight* over sheer benchmark volume — but the comparison must include the robust-MCDA family.

### 4.1 Methods to compare
- **LUR** (and stochastic LUR, Rawlsian LUR).
- **Classical post-processing:** TOPSIS, CP(p=2), knee, ASF, random-weight scalarization.
- **Robust-MCDA (essential additions):** an **SMAA**-based recommendation; an **ROR/UTA**-based recommendation; a **robust/minimax-regret scalarization**.

### 4.2 Problems / data
- Keep **DTLZ/WFG** at `m ∈ {3,5,8,10}` as controlled candidate-set generators (frame them as *test instances*, not EA studies).
- Add a **second real decision dataset** if feasible (e.g., a published MCDA benchmark) so the paper isn't single-application.
- Deepen the **smart-grid** case into the headline decision study (§3.3).

### 4.3 Protocol (mandatory where randomness exists)
- **≥30 replications**; report median + IQR or mean ± std — never bare points.
- **Wilcoxon** (pairwise) and **Friedman + Nemenyi/Holm** (multiple), with p-values and effect sizes; mark wins/ties/losses.
- For sampled held-out utilities, report the **distribution** of out-of-class loss with confidence intervals (acceptability-style).

### 4.4 Metrics
- **Decision quality:** cleanly redefined out-of-class loss (non-negative, lower = better); worst-case regret; regret uniformity.
- **Robust-MCDA comparability:** report how often LUR's choice coincides with SMAA's highest-acceptability alternative, and where/why it differs.
- **Cost / scalability:** wall-clock and problem size vs. front-enumeration + post-processing (supports the "direct computability" claim).
- **Sensitivity:** to nadir estimation, θ, probe family, confidence level α.

### 4.5 Ablations (with stats)
- Probe families (singleton/mean/max/full/clustered/PCA-nonneg); reduction quality-cost across all instances; stochastic vs. deterministic; stakeholder/Rawlsian variant.

### 4.6 Reproducibility artifact
- Anonymized repo: source, seeds, configs, environment lockfile, one-command regeneration of every table/figure; hardware stated; short "Reproducibility" note in the paper.

### 4.7 Self-validation before submission
- Re-derive one results table from raw logs to confirm it matches the manuscript. Re-check every theorem against its proof (esp. Thm 5). Search the MCDA literature for a counterexample to each "only method that…" claim and soften accordingly.

---

## 5. Manuscript structure & formatting (EJOR)

- **Elsevier `elsarticle` LaTeX** (single-column review format is fine), convert from Markdown.
- **≤30 pages** all-inclusive — enforce early; move extended proofs and full result tables to an **online appendix/e-companion**.
- Suggested structure: Introduction (with explicit *Contribution to OR*) → Related work incl. robust MCDA → LUR model & properties → Direct computation → Adaptive probes → Extensions (stochastic, multi-stakeholder) → Computational experiments → **Decision-support case study** → Discussion/limitations → Conclusions (with practical/analyst implications) → References → Online appendix.
- Add a **highlights** list and ensure the abstract names the OR contribution and the decision-support payoff.
- Declare data/code availability and any AI-use per current Elsevier policy.

---

## 6. Cover letter & suggested handling

- **Cover letter (first paragraph decides the desk gate):** state (1) the new OR contribution — a regret-based robust-MCDA recommender with an auditable certificate, dominated-exclusion and stability guarantees, and front-free computation; (2) explicit fit to the **Decision Support** area; (3) the three headline results (superior held-out decision quality vs. classical *and* robust-MCDA baselines; lower computational cost than enumerate-then-select; a real decision-support case with managerial insight). Confirm originality/no concurrent submission and ≤30 pages.
- **Suggest handling editor / reviewers** from the MCDA / robust-MCDA community whose work you now cite and contrast (the SMAA, ROR/UTA, PRO, and outranking spheres). Name conflicts of interest.

---

## 7. Timeline

EJOR gives fast desk decisions (often <1 week), so a clean, well-positioned submission is rewarded quickly. Realistic prep for a competitive submission: **~3–5 weeks** (positioning + robust-MCDA baselines + replicated experiments + case study + length/English/reproducibility). A rushed submission of the current draft would most likely desk-reject within days — the positioning work is the difference between a one-week reject and a real shot.

---

## 8. Prioritized checklist

**Must-do (acceptance-critical):**
- [ ] Add robust-MCDA positioning: SMAA, ROR/UTA/GRIP, PRO, regret-in-MCDA; differentiation table.
- [ ] Explicit "Contribution to OR" statement in intro + abstract + highlights.
- [ ] Redefine out-of-class loss cleanly (non-negative, lower = better); link to acceptability indices.
- [ ] Add robust-MCDA baselines (SMAA / ROR / robust-regret scalarization) to all comparisons.
- [ ] ≥30 replications + Wilcoxon/Friedman + dispersion + effect sizes wherever randomness exists.
- [ ] Deepen smart-grid into a narrative decision-support case with managerial insight.
- [ ] Expand bibliography to ~45–70 current MCDA/EJOR refs.
- [ ] Fit ≤30 pages; build online appendix; `elsarticle` formatting; fill author metadata.
- [ ] Professional English pass (desk-reject risk).
- [ ] Public reproducible artifact regenerating every table/figure.
- [ ] Decision-Support-area cover letter + suggested editor/reviewers.

**Should-do:**
- [ ] Second real MCDA dataset for generality.
- [ ] Nadir-estimation and θ sensitivity studies.
- [ ] Cost/scalability vs. enumerate-then-select.
- [ ] Reframe trivial theorems as lemmas; tighten Thm 5.

**Nice-to-have:**
- [ ] Expanded multi-stakeholder/Rawlsian case.
- [ ] Interactive certificate demo linked from the repo.

---

*Bottom line: at EJOR the idea fits and the theory holds — acceptance hinges on positioning LUR convincingly against the robust-MCDA literature (especially SMAA), stating the OR contribution explicitly, and lifting the empirical and bibliographic rigor to OR-journal standard within 30 pages. Do the positioning first; it is the highest-probability lever.*
