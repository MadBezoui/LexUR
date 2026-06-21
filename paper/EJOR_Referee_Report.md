> **Revision status (latest pass).** Mechanical/consistency items now resolved in source: CI numbers reconciled; solver-call counts made consistent; broken "Appendix A" proof references removed; switched to `elsarticle[review]`; author block anonymized. **Fixed in this session:** stale Figure 2 regenerated at CD = 0.178 (`scripts/regen_cd_protocol.py`); "Appendix Appendix A" doubling patched (`\ref` instead of `Appendix~\ref`); family-table Chebyshev/aug.-ASF near-identity explained in the caption (it is a correct consequence of the 0.05 augmentation, not a bug); de-anonymising GitHub URL blinded. Edited source compiles cleanly. **Still outstanding (substantive, require new work):** items 3.1–3.3 below — no regime where LexUR measurably beats ASF/MMR; redundancy edge not shown vs ASF; interval-robust LexUR still unimplemented/unbenchmarked. Recommendation remains **major revision** on those grounds.

---

# Referee Report — European Journal of Operational Research

**Manuscript:** *Beyond Pareto Fronts: A Leximax Universal-Regret Core for Robust Multicriteria Decision Support*

**Recommendation:** Major revision

---

## 1. Summary

The paper proposes the **Leximax Universal-Regret (LexUR) core**, a selection rule for multicriteria decision analysis (MCDA). Given a candidate set and a *declared* family of admissible monotone "probes" (scalar questions over normalised criteria), LexUR computes, for each alternative, a vector of normalised disappointments across the probes, sorts it descending, and recommends the lexicographic-minimax (leximin) alternative together with an interpretable certificate naming the binding probes. The authors prove existence/completeness, weak and strict Pareto compatibility (the latter under a separation condition), a margin-based stability result for the tolerance rule, and a probe-perturbation bound. They give an adaptive correlation-clustering probe construction that keeps the family linear in the number of criteria, and a broadened, frozen benchmark (≈7,200 paired instances, 11 methods, 10 held-out preference families, 8 geometries, m up to 20) plus a synthetic smart-grid dispatch case study. A reproducibility package is released.

The manuscript is well written, unusually candid about its own limitations, and methodologically careful (frozen protocol, claim-evidence matrix, threats-to-validity section). These are genuine strengths and reflect good scientific practice. My reservations are about **the magnitude and demonstrability of the contribution** rather than its honesty.

---

## 2. Assessment of significance and novelty

The motivating observation — that Pareto efficiency is a "safety filter," and post-hoc selection re-injects hidden preferences — is sound and well argued. The framing of the output as a *certificate* rather than a single point is attractive.

However, the core construction is, at bottom, **leximin/ordered-minimax over a family of monotone aggregation functions of normalised regret.** Each ingredient is established: ordered/leximin aggregation (Ogryczak; Yager's OWA), achievement scalarising functions (Wierzbicki), minimax regret (Savage; Kouvelis–Yu), and preference-robust reasoning (SMAA, robust ordinal regression, PRO). The paper's own Proposition (recovery of weighted sum / Chebyshev / lexicographic maximin) confirms that LexUR is a generalisation built from known parts. The theorems, while correct, are light: existence follows from finiteness, Pareto compatibility from monotonicity, and stability from the 1-Lipschitz property of sorting. None is technically deep.

This is acceptable for EJOR **only if the empirical or methodological payoff is convincing.** As written, the empirical case is the weakest part of the argument (see §3.1). The reviewers will therefore press hard on "what does LexUR demonstrably do that ASF or sampled minimax regret does not?" The honest answer in the current manuscript is "produces a certificate and slightly reduces redundancy bias" — and even the redundancy advantage is not clearly established (§3.2). The paper needs to make the *distinctive* contribution land harder, not just qualify it.

---

## 3. Major concerns

### 3.1 The headline empirical result undercuts the thesis
By the authors' own reporting, LexUR is *non-inferior* to ASF and MMR with negligible effect size (Cliff's δ ≤ 0.015), **slightly behind them in average rank**, and **worse than the averaging methods on mean loss**. So on the central quantitative metric LexUR does not beat the best robust scalarisations; it ties them. A top-tier OR journal will ask why a new rule is warranted when an existing one (ASF) matches it on tail loss, beats it on average rank, and is simpler. The paper must either (a) identify a regime where LexUR *measurably* wins, or (b) reposition explicitly as a contribution about *auditability/explanation* and then evaluate that claim directly (it currently does not — interpretability is asserted, never tested with users or against alternative explanation methods such as ASF reference-point sweeps or SMAA acceptability maps).

### 3.2 The redundancy advantage is not clearly demonstrated
Reduced redundancy bias is offered as a key differentiator, but in Table 6 (redundant-objective benchmark) **ASF achieves grouped loss 0.266 vs LexUR's 0.268 and beats LexUR on tail (0.406 vs ... MMR 0.387 is best)**. ASF therefore matches or beats LexUR on the very benchmark designed to showcase LexUR's strength. The advantage shown is over *averaging/Monte-Carlo* methods (TOPSIS, SMAA), which is unsurprising and not the relevant comparison. Please add a comparison that isolates the clustering mechanism (e.g., LexUR-with-clustering vs LexUR-without, and vs ASF) so the *marginal* value of the adaptive probe family is visible.

### 3.3 The recommended robust mode (interval-robust LexUR) is not evaluated
The nadir-stability gate is a **CHECK**, with winner flip-rates of 47–93% under 5–30% nadir error (Table 9). The Discussion concludes that the "primary robust deliverable" is therefore a *stability set* computed over conservative interval bounds (interval-robust LexUR), declared "mandatory" when stability is required. But interval-robust LexUR is **never implemented or benchmarked** in the experiments — the entire empirical study uses empirical point-estimate bounds over the candidate set. The paper thus recommends a mode it does not test, while testing a mode it says should not be relied upon. This is the single most important gap: implement interval-robust LexUR and report stability-set size, coverage, and held-out loss. Without it, the practical recommendation is unsupported.

### 3.4 IIA failexure plus set-dependence weakens the "unique recommendation" claim
The authors correctly note (Discussion) that LexUR violates Independence of Irrelevant Alternatives because both normalisation bounds and probe anchors are computed over the active set A. Combined with the nadir sensitivity, the "exact lexicographic minimiser" is fragile to set composition. The candor is commendable, but the cumulative effect is that the exact point recommendation — the headline object — is unstable, and the stable fallback (3.3) is untested. The paper needs to resolve this tension, not just document it.

### 3.5 The continuous / front-free formulation is underdeveloped
For an EJOR (OR-optimisation) audience, the front-free continuous formulation is the most interesting angle, yet it is presented as "future work," with only a few solver-call counts and no formulation in the appendix. Worse, the reported counts are inconsistent (see §4): "19 vs 150" solver calls in §7.2 and Table 5, "12 restricted LP calls" later in §7.2, and "4 vs 60" in Table 5. Either develop this properly (give the ordered-value linearisation explicitly, characterise when the 2K anchor subproblems are tractable, benchmark against generate-then-select on a real MOP/MILP) or substantially trim the claims. As is, it reads as overclaiming relative to evidence.

### 3.6 Entirely synthetic validation
All fronts (DTLZ-style), utilities, and the smart-grid case are synthetic. EJOR increasingly expects at least one real MCDA dataset or genuine application. The smart-grid study is illustrative only (NSGA-II-generated candidates on a synthetic IEEE-14-derived model). At minimum, add one real-data MCDA problem; ideally show the certificate adding value in a setting with a real decision maker.

### 3.7 Theory: the stability theorem may be practically vacuous
Theorem 4 (stability under a margin condition) requires a margin Δ that the authors admit "can be restrictive on densely packed candidate sets." Given the observed near-tie behaviour (flip rates above), the conditions of the theorem appear rarely satisfied in exactly the dense settings of the experiments. Please report, empirically, how often the margin condition actually holds on the benchmark instances — otherwise the theorem guarantees stability in a regime that does not occur.

---

## 4. Specific corrections and internal inconsistencies (must fix)

These are concrete and will be caught by reviewers; resolving them pre-emptively will help.

1. **Non-inferiority CI numbers disagree between text and table.** §7.2 text: "upper 95% CI bounds 0.004 and 0.0025" (ASF, MMR). Table 5 gates: "CI upper 0.0015" (ASF) and "0.0021" (MMR). Reconcile.

2. **Direct-computation solver counts are inconsistent.** §7.2 gives "19 solver calls ... vs 150," then "12 restricted LP calls compared to exhaustive generation," while Table 5 lists "19 vs 150; 4 vs 60." Three different figure sets. Clarify which problem each refers to and make them consistent.

3. **Table 6: the "Cheby." and "aug. ASF" columns are identical for every method** (0.511/0.511, 0.458/0.458, 0.434/0.434, 0.442/0.443, 0.454/0.454, ...). Either the two held-out families are effectively the same (in which case do not present them as distinct evidence of breadth) or there is a duplication bug. Explain.

4. **Gate "Stochastic LexUR does not hurt tail loss" reports "risk 0.383 vs 0.383"** — exactly equal. If the stochastic adjustment changes nothing on this metric, say so and clarify what the gate establishes; identical values invite suspicion of a no-op.

5. **Proposition "Recovery of standard scalarisations"** is a set of one-line observations rather than a proposition; consider demoting to a remark, or stating and proving it precisely (the "weighted sum" recovery in particular is immediate from a singleton family).

6. **Broken proof-appendix references (confirmed in the compiled PDF).** In the rendered PDF the appendices are **A = Smart-grid economic dispatch formulation** and **B = Multi-stakeholder (Rawlsian) variant**. There is **no proof appendix.** Yet the intro states "All proofs are in Appendix A," the contributions list cites "(§3, Appendix A)," and §3 says "Proofs are in Appendix A." In fact the proofs are given **inline** after each theorem/lemma in §3 and §5, so the cross-references are simply wrong and, as rendered, point the reader to the smart-grid model. Either move the proofs to a genuine Appendix A or delete every "Appendix A" proof reference and state that proofs are inline. (Table 8's "Smart-grid applicability → Appendix A" row is the only correct Appendix-A reference.)

7. **Figure 2 is stale and contradicts its own caption and text.** §7.2 text and the Figure 2 caption both report **Nemenyi CD = 0.178**, but the embedded CD-diagram image in Figure 2 is printed with **"CD=0.31"** in its top-left corner. The figure was evidently generated from an earlier run and not regenerated after the CD value changed. Regenerate `cd_protocol.pdf` so the plotted CD matches the text (0.178). (Figure 3 / `cd_diagram.pdf` is internally consistent at CD = 0.48.)

8. **Document class.** The source uses `article`; EJOR requires `elsarticle`. The header comment notes this — complete the switch before submission and move abstract/keywords into the elsarticle front matter.

9. **Anonymity / repository link.** Confirm EJOR's current blinding policy. The manuscript carries the author name and affiliation and a de-anonymising GitHub URL (`github.com/MadBezoui/LexUR`). If review is double-blind, anonymise both and deposit a blind copy of the code.

> *Note: this report reviews the actual compiled `main.pdf` (28 pp., CD = 0.178 in text). Items 1–7 above were verified against the rendered PDF, not only the LaTeX source.*

---

## 5. Related work — gaps to address

27 references is light for an EJOR contribution of this scope (typical range 40–60+), and several are textbook-level. Consider adding, where relevant:

- **Robustness in MCDA / decision aiding:** B. Roy's work on robustness concerns in decision aiding; recent surveys on robust MCDA. This is directly on-topic and currently absent.
- **Ordered weighted aggregation:** Torra's WOWA (Yager 1988 is cited, but the ordered-weighting literature is thin); connections between OWA, leximin and your probe family deserve a precise placement.
- **Minimax regret in optimisation under uncertainty:** Kouvelis & Yu (robust discrete optimisation), and the regret-based robust optimisation stream — your "minimax regret" positioning needs these anchors.
- **Recent preference robust optimisation:** Delage & Li, and Vayanos et al., post-date and sharpen Armbruster–Delage (2015) and Hu–Mehrotra (2015).
- **Inverse/disaggregation MCDA:** beyond Doumpos & Zopounidis (2011), the UTA family and recent preference-learning MCDA, to position the "declared probes vs learned preferences" contrast.

---

## 6. Presentation

The writing is clear and the structure logical. The claim-evidence matrix (Table 8), parameter table (Table 7), and threats-to-validity section are exemplary and should be retained. My main stylistic concern is **over-hedging**: the abstract and title ("Beyond Pareto Fronts," "Universal-Regret") promise more than the heavily qualified results deliver, and nearly every empirical claim is immediately walked back. The effect is that the reader struggles to identify the firm contribution. Tighten the framing so the genuine, defensible contribution (auditable robust selection with linear-size probe family) is stated once, clearly, and not undermined paragraph by paragraph.

Minor: the abstract is a single dense block — consider splitting; Table 1 (positioning) is very wide and may overflow the elsarticle column; several figures (sensitivity plots) are referenced in the repo but ensure all appear in the PDF.

---

## 7. Recommendation to the editor

The paper is honest, well-organised, and reproducible, and the certificate idea is appealing. But for EJOR the contribution must be sharpened on at least three fronts before acceptance: (i) demonstrate a regime where LexUR *measurably* outperforms ASF/MMR, or reposition around auditability and evaluate it; (ii) implement and benchmark the interval-robust mode the paper itself declares to be the real deliverable (§3.3); and (iii) resolve the numerical inconsistencies in §4 and develop or trim the continuous formulation. These are substantial but achievable. I recommend **major revision**.
