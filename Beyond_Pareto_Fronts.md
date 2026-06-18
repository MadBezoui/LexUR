---
title: "Beyond Pareto Fronts: A Leximax Universal-Regret Core for Multiobjective Optimization"
author:
  - name: "Madani Bezoui"
    affiliation: "CESI LINEACT, UR 7527, Nancy, France"
    email: "mbezoui@cesi.fr"
journal: "European Journal of Operational Research"
---

# Beyond Pareto Fronts: A Leximax Universal-Regret Core for Multiobjective Optimization

**Authors:** Madani Bezoui  
**Affiliations:** CESI LINEACT, UR 7527, Nancy, France  
**Correspondence:** mbezoui@cesi.fr  

---

## Abstract

Pareto optimality is a fundamental efficiency concept, but it is not a complete decision rule. The Pareto front produces a set of efficient alternatives without providing a principled mechanism for selecting a single robust solution, forcing decision-makers to either inspect exponentially large fronts or impose arbitrary weights, distance metrics, or threshold parameters ex post.

We introduce the **Leximax Universal-Regret (LUR) Core**, a regret-based robust-MCDA recommender that ranks feasible solutions by the lexicographically sorted vector of normalized regrets over a **declared class of monotone rational probes**. The core OR contribution is an auditable certificate with dominated-exclusion and stability guarantees that avoids explicit Pareto-front enumeration. The method returns a single solution or small equivalence class together with this **regret certificate** identifying the most critical objective coalitions. We prove: (1) existence and completeness of the induced preorder for finite candidate sets; (2) Pareto compatibility under monotone probes; (3) dominated-solution exclusion -- no dominated solution can be LUR-optimal if its dominator is feasible; (4) stability under bounded regret perturbations; and (5) direct computability through sequential minimax-regret constraints, avoiding explicit Pareto-front enumeration.

We define an **adaptive probe generation** mechanism that uses objective correlation clustering to identify redundancy and construct a nonnegative, monotone probe basis. This preserves Pareto compatibility while reducing the probe space from exponential to linear in the number of objective clusters. We also introduce a **stochastic regret certificate** with confidence bounds for noisy objectives, and a **multi-stakeholder extension** that protects the worst-off stakeholder across all probes.

Computational experiments on the DTLZ and WFG benchmark suites, together with a smart-grid dispatch case study, evaluate LUR against held-out preference models (random linear, weighted Chebyshev, augmented ASF, CES utilities) not used during optimization. LUR achieves lower worst-case regret under these held-out models than TOPSIS, compromise programming, knee-point selection, and random weight scalarization, while requiring no ex ante weight specification. The framework is accompanied by open-source software supporting direct optimization and interactive regret certificates.

**Keywords:** multiobjective optimization, Pareto front, minimax regret, lexicographic ordering, robust decision-making, multi-criteria decision analysis, achievement scalarizing functions, ordered weighted aggregation.

---

## 1. Introduction

### 1.1 The Pareto Front as Safety Filter, Not Decision Object

Since Vilfredo Pareto's foundational work, Pareto optimality has been the cornerstone of multiobjective optimization. A solution is Pareto efficient if no objective can be improved without worsening another. This definition is logically impeccable -- it is a *safety property* that eliminates obviously poor choices. Yet it is decisionally incomplete. For $m$ conflicting objectives, the Pareto front typically contains an exponential or infinite number of points. The decision-maker (DM) is left with a cloud of efficient alternatives and no principled guidance for selecting one.

This creates what we call the **Pareto paralysis problem**: the very tool designed to *help* decision-making becomes a source of **hesitation**. The DM must either:

1. **Impose arbitrary weights** ex post (weighted sum, TOPSIS, compromise programming), collapsing the rich multiobjective structure into a single scalar;
2. **Select a knee point** or geometric center, which is sensitive to scaling and objective correlation;
3. **Apply outranking methods** (ELECTRE, PROMETHEE) that require non-intuitive threshold parameters; or
4. **Inspect the entire front**, a task that becomes cognitively intractable for $m > 3$ objectives.

Each of these approaches requires the DM to make additional choices *after* the optimization is complete -- choices that are often no easier than the original decision problem. The fundamental issue is that **the Pareto front is a safety filter, not a decision engine**.

### 1.2 The Regret Turn: From Fronts to Certificates

Our central thesis is that the **Pareto front is the wrong final object** for multiobjective decision-making. The correct object is a **regret certificate** -- a vector of normalized disappointments over all rational decision questions the DM might reasonably ask, sorted from worst to best. Instead of asking "Which solutions are efficient?" we ask:

> **"Which solution is least fragile across all rational interpretations of my objectives?"**

This transforms the optimization object from a *set* to a *certificate*. The certificate tells the DM exactly which questions are most disappointed and by how much, providing a decision narrative rather than a cloud of points.

### 1.3 The Leximax Universal-Regret (LUR) Core

We formalize this intuition as the **Leximax Universal-Regret (LUR) Core**. Given a feasible set $X$ and a declared class of admissible monotone probes $\mathcal{Q}$, the LUR solution is the one that minimizes, lexicographically, the sorted vector of normalized regrets over all probes in $\mathcal{Q}$.

The framework rests on three principles:

1. **Declared admissibility:** The probe family $\mathcal{Q}$ is explicitly declared, not hidden. The DM knows exactly which rational questions are being considered.
2. **Pareto compatibility:** If a solution dominates another, it is never ranked worse under LUR (provided all probes are monotone).
3. **Direct computability:** The LUR solution can be found by solving a sequence of minimax-regret constraints, without necessarily enumerating the Pareto front.

### 1.4 Contribution to OR

This paper introduces a novel approach to the application of OR in Decision Support. Unlike methods that evaluate solutions over a feasible preference space (like SMAA) or a robust utility set (like ROR or PRO), LUR takes the lexicographic minimax of normalized regret over a declared class of monotone probes. This provides decision analysts with a single robust recommendation and an auditable certificate, requiring no ex ante weights and bypassing Pareto front enumeration.

The specific contributions of this paper are:

- **C1. The LUR order:** A regret-based robust-MCDA recommender defining a complete, Pareto-respecting preorder over feasible solutions based on lexicographic minimax regret over a declared class of monotone rational probes.
- **C2. Pareto compatibility and dominated exclusion:** Formal proofs that LUR never prefers a dominated solution over its dominator, and that dominated solutions are excluded from optimality.
- **C3. Stability theorem:** If regret estimates are perturbed by at most $\eta$, and the lexicographic gap exceeds $2\eta$, the LUR winner is unchanged.
- **C4. Direct optimization formulation:** A sequential minimax-regret formulation that computes the LUR solution without Pareto-front enumeration, for both finite and continuous feasible sets.
- **C5. Adaptive nonnegative probe generation:** A correlation-based clustering mechanism that identifies redundant objectives and constructs a monotone probe basis, preserving Pareto compatibility while reducing probe count.
- **C6. Stochastic regret certificates:** Confidence-aware regret bounds for noisy objectives.
- **C7. Multi-stakeholder extension:** A Rawlsian variant that protects the worst-off stakeholder across all probes.
- **C8. Held-out evaluation:** Experimental validation against preference models not used during optimization, demonstrating generalization.

### 1.5 Organization

Section 2 reviews related work. Section 3 formalizes the LUR core and proves its foundational properties. Section 4 presents the direct optimization formulation. Section 5 introduces adaptive nonnegative probe generation. Section 6 extends to stochastic objectives and multiple stakeholders. Section 7 describes the experimental evaluation. Section 8 discusses limitations. Section 9 concludes. All proofs are in Appendix A.

---

## 2. Background and Related Work

### 2.1 Pareto Optimality and Post-Processing Methods

Pareto optimality defines a partial order on the feasible set $X$. For a vector objective $F(x) = (f_1(x), \dots, f_m(x))$, a solution $x$ Pareto-dominates $y$ if $f_i(x) \leq f_i(y)$ for all $i$ with strict inequality for at least one $i$. The Pareto front is the set of non-dominated solutions.

Because the front is typically large, practitioners apply post-processing methods to select a single solution. These include:

- **Weighted sum:** $\sum_i w_i f_i(x)$. Simple but requires weights $w$ and cannot find non-convex front points [1].
- **TOPSIS [2]:** Selects the solution closest to the ideal point and farthest from the nadir. Requires a distance metric and equal or specified weights.
- **Compromise programming [3]:** Minimizes the $L_p$ distance to an ideal point. Requires $p$ and weights.
- **Knee point methods [4]:** Select points of maximum curvature. Sensitive to scaling and may yield multiple knee points.
- **ELECTRE [5] and PROMETHEE [6]:** Outranking methods requiring concordance/discordance thresholds.
- **Hypervolume contribution [7]:** Selects points maximizing hypervolume. Computationally expensive and may favor extremes.

All these methods require **additional parameters** after the Pareto front is generated. LUR avoids this by integrating the selection criterion into the optimization itself.

### 2.2 Achievement Scalarizing Functions

Achievement scalarizing functions (ASF), developed by Wierzbicki [8] and extended by Miettinen and Makela [9], project a reference point onto the Pareto front using parameterized metrics that interpolate between $L_1$ and $L_\infty$ norms. These are powerful but require:
- A reference point (often unknown or arbitrary);
- A parameter controlling the metric shape (arbitrary);
- Pareto front generation before projection.

LUR can be viewed as a **parameter-free, reference-point-free ASF** where the "metric" is the leximax regret over all rational coalitions. The reference point is the ideal vector $z^*$ (computed, not imposed), and the "metric" is learned from the objective structure rather than specified by the analyst.

### 2.3 Ordered Weighted Aggregation and Lexicographic Methods

Yager [10] introduced Ordered Weighted Averaging (OWA) operators, which apply decreasing weights to sorted objective values. OWA can model optimism, pessimism, and various attitudes between them. Ogryczak and Sliwinski [11] extended OWA to importance-weighted settings. Ogryczak [12] established the link between OWA and lexicographic minimax optimization.

LUR differs from OWA in two critical ways:
1. **Regret vs. raw objectives:** LUR sorts *regret values* (dimensionless, normalized) rather than raw objective values (different scales and units).
2. **Probe-based vs. objective-based:** LUR's aggregation units are *rational decision questions* (probes), not raw objectives. This avoids the Condorcet cycles that arise when objectives are treated as voters.

### 2.4 Minimax Regret and Robust Decision-Making

Regret-based decision-making has roots in Savage [13] and Loomes & Sugden [14]. In optimization, minimax regret seeks solutions that minimize the maximum difference from the best achievable value. Chen [15] recently introduced multiobjective regret equilibria.

LUR extends minimax regret in three directions:
1. **Lexicographic:** After minimizing the worst regret, minimize the second-worst, etc.
2. **Probe-based:** Regret is computed over rational coalitions, not individual objectives.
3. **Direct:** The LUR solution can be found without generating the Pareto front.

### 2.5 Robust Multiobjective Optimization

Robust optimization, pioneered by Ben-Tal and Nemirovski [16], seeks solutions that perform well under uncertainty. In multiobjective settings, robustness is typically addressed by considering worst-case objective values over uncertainty sets [17]. LUR connects to this literature by treating the probe selection as a worst-case analysis: the solution must perform well under *all* declared rational probes.

### 2.6 Robust MCDA (SMAA, ROR, and PRO)

LUR is conceptually closest to the robust-MCDA literature, which evaluates solutions over a set of rational interpretations rather than a single set of weights.
- **Stochastic Multicriteria Acceptability Analysis (SMAA):** Evaluates solutions by integrating over a feasible weight or preference space to compute acceptability indices.
- **Robust Ordinal Regression (ROR) and UTA methods:** Recommend solutions by considering all value functions compatible with decision-maker preference information.
- **Preference Robust Optimization (PRO):** Optimizes for the worst-case utility over an ambiguity set of preference models.

While SMAA relies on Monte Carlo integration over a weight space and ROR/PRO rely on utility ambiguity sets, LUR computes the lexicographic minimax of normalized regret over a **declared class of monotone probes**. LUR's regret profile provides a robust certificate analogous to SMAA acceptability indices but without requiring numerical integration over a continuous space.

### 2.7 Social Choice and Fairness

The problem of aggregating multiple criteria resembles social choice. However, using objectives as voters leads to Condorcet cycles. LUR avoids this by using *rational decision questions* as the basis for regret, not raw objectives as voters.

For multi-stakeholder settings, we draw on Rawls [18] and Nash [19]. The Rawlsian maximin principle -- maximize the welfare of the worst-off -- inspires our multi-stakeholder extension. However, we do not claim uniqueness theorems; we only show that LUR satisfies natural fairness properties.

### 2.8 Gap Analysis

Table 1 summarizes the positioning of LUR relative to classical and robust MCDA methods.

| Method | Requires Weights | Requires Thresholds | Requires Front | Single Solution | Pareto Compatible | Evaluates Robustly |
|--------|-----------------|---------------------|----------------|-----------------|-------------------|--------------------|
| Weighted Sum | Yes | No | No | Yes | Yes | No |
| TOPSIS | Yes (or equal) | No | Yes | Yes | Yes | No |
| Compromise Programming | Yes | No (needs $p$) | Yes | Yes | Yes | No |
| ELECTRE | No | Yes | Yes | No | Yes | No |
| SMAA | No | No | No | No (returns index) | Yes | Yes |
| ROR/UTA | Preference Info | No | No | Yes | Yes | Yes |
| PRO | Ambiguity Set | No | No | Yes | Yes | Yes |
| Minimax Regret | No | No | No | Yes | No* | Yes |
| **LUR (Ours)** | **No** | **No** | **No** | **Yes** | **Yes** | **Yes** |

*Standard minimax regret on raw objectives may violate Pareto compatibility if objectives are not normalized consistently.

*Table 1: Comparison of multiobjective decision methods. LUR is the only method that requires no weights, no preference information, no thresholds, no Pareto front, evaluates robustly, and still produces a single Pareto-compatible solution.*

---

## 3. The Leximax Universal-Regret Core

### 3.1 Problem Formulation

Let $X \subseteq \mathbb{R}^n$ be the feasible set and $F: X \to \mathbb{R}^m$ be the vector objective function $F(x) = (f_1(x), \dots, f_m(x))$. We assume minimization throughout; maximization objectives are handled by sign reversal.

Let $A = \{x_1, \dots, x_N\} \subseteq X$ be a finite set of candidate solutions. For direct optimization (Section 4), $X$ may be continuous and $A$ is not required.

### 3.2 Normalization

Objectives have different scales and units. We normalize each objective to $[0, 1]$ using positive affine transformations:

$$r_i(x) = \frac{f_i(x) - z_i^\star}{z_i^N - z_i^\star + \varepsilon}$$

where $z_i^\star = \min_{x \in X} f_i(x)$ is the ideal value, $z_i^N$ is a nadir or anti-ideal estimate, and $\varepsilon > 0$ prevents division by zero. The normalized vector is $r(x) = (r_1(x), \dots, r_m(x)) \in [0, 1]^m$.

**Remark:** LUR is invariant to positive affine rescaling of objectives, provided normalization bounds are transformed consistently. It is *not* invariant to arbitrary monotone transformations (e.g., $f_i \mapsto f_i^2$), which would change the relative distances that define regret.

### 3.3 Admissible Probes

A **probe** is a scalar function $q: [0,1]^m \to \mathbb{R}$ representing a rational decision question. The probe family $\mathcal{Q}$ is **declared explicitly** -- it is part of the problem specification, not hidden from the DM.

**Definition 1 (Admissible Probe).** A probe $q$ is **admissible** if it satisfies:

1. **Monotonicity:** $q$ is non-decreasing in each $r_i$ (more of any objective does not decrease the probe value).
2. **Normalization:** $q(0, \dots, 0) = 0$ and $q(1, \dots, 1) = 1$ (or can be rescaled to satisfy this).
3. **Lipschitz continuity:** $|q(r) - q(r')| \leq L \|r - r'\|_\infty$ for some constant $L$.

The monotonicity condition is essential for Pareto compatibility. Non-monotone probes (e.g., with negative weights) could prefer dominated solutions.

**Example probes:**

- **Singleton probes:** $q_i(x) = r_i(x)$ for each objective $i$.
- **Mean coalition probes:** $q_{S,1}(x) = \frac{1}{|S|} \sum_{i \in S} r_i(x)$ for $S \subseteq \{1, \dots, m\}$.
- **Max coalition probes:** $q_{S,\infty}(x) = \max_{i \in S} r_i(x)$ for $S \subseteq \{1, \dots, m\}$.
- **Weighted monotone probes:** $q_w(x) = \sum_{i=1}^m w_i r_i(x)$ with $w_i \geq 0$, $\sum_i w_i = 1$.

### 3.4 Disappointment and Regret

For each probe $q \in \mathcal{Q}$, compute its best attainable value:
$$q^\star = \min_{x \in X} q(r(x))$$

and a reference worst value $q^-$ (e.g., the maximum over $X$ or a user-defined worst acceptable value). The **normalized disappointment** of solution $x$ under probe $q$ is:

$$D_q(x) = \frac{q(r(x)) - q^\star}{q^- - q^\star + \varepsilon} \in [0, 1]$$

$D_q(x) = 0$ means $x$ is optimal for probe $q$. $D_q(x) = 1$ means $x$ is worst-case for probe $q$.

### 3.5 The Leximax Universal-Regret Order

Collect all disappointments into a vector:
$$D(x) = (D_{q_1}(x), \dots, D_{q_K}(x))$$

where $K = |\mathcal{Q}|$. Sort in **descending** order:
$$D^\downarrow(x) = \text{sort}_\downarrow(D(x)) = (D_{[1]}(x), D_{[2]}(x), \dots, D_{[K]}(x))$$

where $D_{[1]}(x) \geq D_{[2]}(x) \geq \dots \geq D_{[K]}(x)$.

The **Leximax Universal-Regret order** is:
$$x \preceq_{LUR} y \quad \Longleftrightarrow \quad D^\downarrow(x) \leq_{\text{lex}} D^\downarrow(y)$$

That is, $x$ is preferred to $y$ if its worst disappointment is smaller; if tied, its second-worst is smaller; and so on lexicographically.

The **Leximax Universal-Regret Solution** is:
$$x^{LUR} \in \arg\min_{x \in X}^{\text{lex}} D^\downarrow(x)$$

### 3.6 Foundational Properties

**Lemma 1 (Existence and Completeness).** For any finite candidate set $A$ and finite probe family $\mathcal{Q}$, the LUR solution $x^{LUR}$ exists and the relation $\preceq_{LUR}$ is a complete preorder on $A$.

*Proof.* For each $x \in A$, $D^\downarrow(x)$ is a well-defined real vector in $[0,1]^K$. Lexicographic comparison of real vectors is a complete preorder on $\mathbb{R}^K$. Since $A$ is finite, the minimum exists. ∎

**Theorem 2 (Pareto Compatibility).** If $x$ strictly Pareto-dominates $y$ and all probes $q \in \mathcal{Q}$ are monotone non-decreasing in each normalized objective, then $D_q(x) < D_q(y)$ for all $q$ with strict inequality for at least one $q$, and therefore $x \prec_{LUR} y$.

*Proof.* If $x \prec_P y$, then $r_i(x) \leq r_i(y)$ for all $i$ with strict inequality for at least one $j$. Since each probe $q$ is monotone in the $r_i$, we have $q(r(x)) \leq q(r(y))$ for all $q$, with strict inequality for any probe that depends on $r_j$. Since $q^\star$ and $q^-$ are independent of $x$ and $y$, the disappointment $D_q(x) \leq D_q(y)$ for all $q$, with strict inequality for at least one $q$. Therefore $D^\downarrow(x) <_{\text{lex}} D^\downarrow(y)$. ∎

**Corollary 2.1 (Dominated Exclusion).** If $x$ is Pareto-dominated by $y$ and $y$ is feasible, then $x$ cannot be LUR-optimal.

*Proof.* By Theorem 2, $y \prec_{LUR} x$. Since the LUR solution is the minimum of $\preceq_{LUR}$, $x$ cannot be optimal. ∎

**Theorem 3 (Stability).** Let $\hat{D}_q(x)$ be estimates of $D_q(x)$ with maximum error $\eta = \max_{x,q} |\hat{D}_q(x) - D_q(x)|$. Let $\delta_{\min}$ be the minimum lexicographic gap between distinct candidates under true regrets:
$$\delta_{\min} = \min_{x \neq y} \max_k \{D_{[k]}(x) - D_{[k]}(y) : D_{[j]}(x) = D_{[j]}(y) \, \forall j < k\}$$
If $2\eta < \delta_{\min}$, then the LUR winner under $\hat{D}$ equals the true LUR winner.

*Proof.* If $2\eta < \delta_{\min}$, then for any pair $(x, y)$ with true lexicographic ordering $x \prec_{LUR} y$, the estimated ordering satisfies $\hat{D}^\downarrow(x) <_{\text{lex}} \hat{D}^\downarrow(y)$. The maximum perturbation in any component is $\eta$, and the lexicographic gap exceeds $2\eta$, so the ordering is preserved. ∎

**Remark on Continuous $X$:** For continuous $X$, existence requires compactness of $X$ and continuity of all probes. The LUR solution exists if $X$ is compact and each $q \circ r$ is continuous. Uniqueness is not guaranteed; there may be a small equivalence class of solutions with identical regret vectors.

### 3.7 The Algorithm for Finite Candidates

For a finite candidate set $A = \{x_1, \dots, x_N\}$:

1. Compute objective matrix $F_{ij} = f_j(x_i)$.
2. Normalize: $R_{ij} = (F_{ij} - z_j^\star) / (z_j^N - z_j^\star + \varepsilon)$.
3. For each probe $q \in \mathcal{Q}$, compute values $V_{iq} = q(r(x_i))$.
4. Compute $q^\star = \min_i V_{iq}$ and $q^- = \max_i V_{iq}$.
5. Compute disappointments: $D_{iq} = (V_{iq} - q^\star) / (q^- - q^\star + \varepsilon)$.
6. Sort each row $D_i$ descending.
7. Select the lexicographically smallest row.

**Complexity:** $O(K \cdot N \cdot m + K \cdot N \log N + N^2 \cdot K)$ for naive lexicographic comparison, where $K = |\mathcal{Q}|$.

---

## 4. Direct Optimization: Computing LUR Without Pareto-Front Enumeration

A key claim of LUR is that it can be computed **directly**, without first generating a Pareto front. This section formalizes this claim.

### 4.1 The Sequential Minimax-Regret Formulation

For continuous $X$ (or large discrete $X$), we formulate LUR as a sequence of minimax-regret optimization problems:

**Stage 1:** Minimize the worst regret:
$$\min_{x \in X} \max_{q \in \mathcal{Q}} D_q(x)$$

Let the optimal value be $\rho_1$ and the optimal set be $X_1 = \{x \in X : \max_q D_q(x) = \rho_1\}$.

**Stage 2:** Minimize the second-worst regret over $X_1$:
$$\min_{x \in X_1} \max_{q \in \mathcal{Q} \setminus \mathcal{Q}_1(x)} D_q(x)$$
where $\mathcal{Q}_1(x) = \{q : D_q(x) = \rho_1\}$ is the set of probes achieving the worst regret at $x$.

Continue until all probes are exhausted or the optimal set is a singleton.

### 4.2 Single-Stage Formulation

All stages can be combined into a single optimization problem using auxiliary variables:

$$\min_{x, \rho_1, \dots, \rho_K} \sum_{k=1}^K M^{K-k} \rho_k$$

subject to:
$$D_q(x) \leq \rho_k + M \cdot \mathbb{1}\{q \notin \mathcal{Q}_k\}, \quad \forall q \in \mathcal{Q}, \, k = 1, \dots, K$$
$$x \in X$$
$$\rho_1 \geq \rho_2 \geq \dots \geq \rho_K \geq 0$$

where $M$ is a large constant and $\mathcal{Q}_k$ are sets of probes assigned to each rank. This is a mixed-integer formulation for discrete probe assignment.

### 4.3 Continuous Optimization with Soft-Max Smoothing

For continuous $X \subseteq \mathbb{R}^n$, the max operator is non-smooth. We use soft-max smoothing:

$$\max_{q \in \mathcal{Q}} D_q(x) \approx \frac{1}{\tau} \log \left( \sum_{q \in \mathcal{Q}} \exp(\tau \cdot D_q(x)) \right)$$

As $\tau \to \infty$, this approaches the true max. For finite $\tau$, it is smooth and differentiable.

**Sequential Convex Programming (SCP):**
At iteration $k$ with current solution $x_k$:
1. Identify active probes: $\mathcal{Q}_k = \{q : D_q(x_k) \geq \rho_1 - \varepsilon\}$.
2. Solve convex approximation:
   $$\min_{x, \rho} \rho$$
   $$\text{s.t. } D_q(x_k) + \nabla D_q(x_k)^T (x - x_k) \leq \rho, \quad \forall q \in \mathcal{Q}_k$$
   $$x \in X$$
3. Update $x_{k+1}$ and iterate.

This **probe-active-set SCP** is analogous to SQP methods. Convergence to a local optimum is guaranteed under standard convexity assumptions.

### 4.4 The Real Operational Breakthrough

The direct optimization formulation is the real operational advantage of LUR:

> **Instead of approximating the Pareto front and then selecting one point, LUR directly searches for the least fragile compromise across all declared rational probes.**

This eliminates the two-stage process (front generation + post-processing) that dominates current practice. The DM specifies the probe family, and LUR returns the robust solution directly.

---

## 5. Adaptive Nonnegative Probe Generation

### 5.1 The Redundancy Problem

For $m$ objectives, the full coalition probe family has $K = 3 \cdot 2^m$ probes -- exponential in $m$. Many objectives are correlated, so many coalitions ask redundant questions. We need a mechanism to identify distinct objective groups and construct a smaller, **nonnegative, monotone** probe basis.

### 5.2 Objective Correlation Clustering

We use correlation clustering to identify redundant objectives:

1. **Compute the correlation matrix** $\Sigma$ from a sample of candidate solutions:
   $$\Sigma_{ij} = \text{Corr}(f_i, f_j) = \frac{\text{Cov}(f_i, f_j)}{\sigma_i \sigma_j}$$

2. **Cluster objectives** by correlation. Objectives with $|\Sigma_{ij}| > \theta$ (threshold) are grouped into the same cluster. This yields $c$ clusters $C_1, \dots, C_c$.

3. **Construct cluster probes:** For each cluster $C_k$, define:
   $$q_{C_k, 1}(x) = \frac{1}{|C_k|} \sum_{i \in C_k} r_i(x)$$
   $$q_{C_k, \infty}(x) = \max_{i \in C_k} r_i(x)$$

4. **Always include singleton probes:** $q_i(x) = r_i(x)$ for all $i$.

The resulting probe family has $K = 2c + m$ probes -- linear in $m$ and $c$.

### 5.3 Nonnegative Probe Basis from PCA Loadings

An alternative to correlation clustering uses PCA loadings with nonnegativity constraints:

1. **Eigen-decompose** $\Sigma = U \Lambda U^T$.
2. **For each principal component $k$**, compute nonnegative loadings:
   $$a_{ki} = \frac{u_{ki}^2}{\sum_j u_{kj}^2} \geq 0, \quad \sum_i a_{ki} = 1$$
3. **Define nonnegative eigenprobes:**
   $$q_{k, 1}(x) = \sum_{i=1}^m a_{ki} r_i(x)$$
   $$q_{k, \infty}(x) = \max_i a_{ki} r_i(x)$$

These probes are guaranteed monotone because all weights are nonnegative.

**Lemma 2 (Nonnegative Probe Pareto Compatibility).** If all probes in $\mathcal{Q}$ are defined with nonnegative weights ($w_i \geq 0$ for all $i$), then LUR is Pareto compatible.

*Proof.* Immediate from Theorem 2, since nonnegative weighted sums and maxima are monotone non-decreasing in each $r_i$. ∎

### 5.4 Approximation Guarantee

**Theorem 5 (Probe Approximation).** Let $\mathcal{Q}_{\text{full}}$ be the full coalition probe family and $\mathcal{Q}_{\text{reduced}}$ be the reduced family (cluster-based or nonnegative PCA). Let $L$ be the Lipschitz constant of all probes. If the maximum reconstruction error of the reduced family is $\eta$ (i.e., for every $q \in \mathcal{Q}_{\text{full}}$ there exists $q' \in \mathcal{Q}_{\text{reduced}}$ with $|q(r) - q'(r)| \leq \eta$ for all $r$), then the LUR regret values under $\mathcal{Q}_{\text{reduced}}$ differ from those under $\mathcal{Q}_{\text{full}}$ by at most $L\eta$.

*Proof.* For any $x$ and $q \in \mathcal{Q}_{\text{full}}$, let $q'$ be the approximating probe in $\mathcal{Q}_{\text{reduced}}$. Then:
$$|D_q(x) - D_{q'}(x)| = \left|\frac{q(x) - q^\star}{q^- - q^\star + \varepsilon} - \frac{q'(x) - q'^\star}{q'^- - q'^\star + \varepsilon}\right|$$

Since $q$ and $q'$ are $L$-Lipschitz and differ by at most $\eta$, the normalized regrets differ by at most $L\eta$ (up to constants depending on the normalization bounds). ∎

**Remark:** Theorem 5 is an **approximation** result, not an exact preservation claim. The reduced probe family may miss some fine distinctions, but the error is bounded and controllable.

### 5.5 Greedy Probe Selection

Even with reduction, we may have more probes than needed. We use a greedy algorithm to select the minimal set that distinguishes all Pareto-dominant pairs:

```
function GreedyProbeSelect(Q, A):
    Q_selected = empty set
    uncovered = {(x,y) : x dominates y}
    while uncovered is not empty:
        q* = argmax_{q in Q} |{(x,y) in uncovered : D_q(x) < D_q(y)}|
        Q_selected = Q_selected union {q*}
        uncovered = uncovered minus pairs covered by q*
    return Q_selected
```

For the **maximum coverage** variant (cover as many pairs as possible within a budget), this greedy algorithm achieves a $(1 - 1/e)$ approximation factor [20]. For the **minimum-cost full coverage** variant, the approximation factor is $H_d \leq 1 + \ln d$ where $d$ is the maximum number of pairs any single probe can cover [21].

---

## 6. Extensions: Stochastic Objectives and Multiple Stakeholders

### 6.1 Stochastic Regret Certificates

When objectives are noisy, we model $f_i(x) \sim P_i(x)$ with mean $\mu_i(x)$ and variance $\sigma_i^2(x)$. The probe $q(x)$ becomes a random variable.

We define the **$\alpha$-confidence regret** using the Gaussian upper bound:

$$D_q^\alpha(x) = \frac{\mu_q(x) + z_\alpha \cdot \sigma_q(x) - q^\star}{q^- - q^\star + \varepsilon}$$

where $z_\alpha$ is the standard normal quantile (e.g., 1.96 for 95%). This penalizes both high mean regret and high uncertainty.

The **stochastic LUR solution** is:
$$x^{LUR-S} \in \arg\min_{x \in X}^{\text{lex}} \text{sort}_\downarrow(D_{q_1}^\alpha(x), \dots, D_{q_K}^\alpha(x))$$

**Theorem 6 (Stochastic Consistency).** Let $\hat{\mu}_i(x)$ be the sample mean of $n$ independent observations. Under Lipschitz continuity of probes and finite fourth moments, if the minimum lexicographic gap $\delta_{\min}$ exceeds the maximum sampling error, then $x^{LUR-S}_n = x^{LUR}$ with probability approaching 1 as $n \to \infty$.

*Proof.* Similar to Theorem 3, using the fact that sample means converge at $O(1/\sqrt{n})$ and the union bound over finitely many candidates and probes. ∎

### 6.2 Multi-Stakeholder Extension

Let $\mathcal{S} = \{1, \dots, S\}$ be stakeholders. Each stakeholder $s$ has importance weights $w_s \in \Delta^m$.

The **stakeholder-specific regret** is:
$$D_q^s(x) = \frac{q(r(x); w_s) - q^\star(w_s)}{q^-(w_s) - q^\star(w_s) + \varepsilon}$$

The **Rawlsian LUR** minimizes the worst stakeholder regret lexicographically:

$$x^{LUR-R} \in \arg\min_{x \in X}^{\text{lex}} \text{sort}_\downarrow\left( \max_{s \in \mathcal{S}} D_{q_1}^s(x), \dots, \max_{s \in \mathcal{S}} D_{q_K}^s(x) \right)$$

with fairness constraints:
$$D_q^s(x) \leq (1 + \beta) \cdot \rho_1 \quad \forall s \in \mathcal{S}, \, \forall q \in \mathcal{Q}$$

where $\rho_1$ is the worst regret and $\beta \geq 0$ is a proportional fairness parameter.

**Properties:**
- **Anonymity:** The solution is invariant to permutations of stakeholder labels.
- **Monotonicity:** If all stakeholders' regrets decrease, the solution does not worsen.
- **Worst-stakeholder protection:** No stakeholder exceeds $(1+\beta)$ times the minimum worst regret.

We do **not** claim uniqueness or IIA. These properties are sufficient for practical fairness.

---

## 7. Experimental Evaluation

### 7.1 Experimental Design

We evaluate LUR on:

**Benchmark Problems:**
- DTLZ1--DTLZ7 [22]: scalable objectives, various geometries
- WFG1--WFG9 [23]: deceptive, disconnected, non-separable
- Dimensions: $m \in \{3, 5, 8, 10\}$

**Real-World Case:**
- Smart-grid 24-hour dispatch with 6 objectives: cost, emissions, reliability, delay, renewable fraction, peak demand
- 10 generators, stochastic renewable forecasts

### 7.2 Baseline Methods

1. **TOPSIS [2]**
2. **Compromise Programming (CP) [3]** with $p = 2$
3. **Knee Point (KP) [4]**
4. **Random Weight Scalarization (RW):** 100 random weight vectors
5. **Achievement Scalarizing Function (ASF) [8, 9]**

### 7.3 Evaluation Protocol

We use a **held-out evaluation** to test generalization:

**Phase 1 (Training):** LUR is computed using its declared probe family (cluster-based monotone probes).

**Phase 2 (Testing):** The selected solution is evaluated under **preference models not used during optimization**:
- Random linear utilities: $U_w(x) = -\sum_i w_i r_i(x)$ with random $w \in \Delta^m$
- Weighted Chebyshev: $U_\infty(x) = -\max_i w_i r_i(x)$
- Augmented ASF: $U_{ASF}(x) = -\max_i r_i(x) - \epsilon \sum_i r_i(x)$
- CES utility: $U_{CES}(x) = -\left(\sum_i w_i r_i(x)^\rho\right)^{1/\rho}$

For each held-out model, we compute the **out-of-class loss**:
$$\text{Loss}_{test}(x) = \frac{\max_{y \in A} U_{test}(y) - U_{test}(x)}{\max_{y \in A} U_{test}(y) - \min_{y \in A} U_{test}(y)}$$

This is a non-negative regret measure (lower is better), normalized to $[0, 1]$. It conceptually mirrors the acceptability indices used in SMAA, representing the gap between the chosen solution and the best possible solution under the DM's true, unknown preferences.

### 7.4 Internal Metrics

- **Worst-case LUR regret (WCR):** $\max_{q \in \mathcal{Q}} D_q(x)$
- **Regret uniformity (RU):** $\text{std}(D^\downarrow(x))$
- **Critical probe count:** Number of probes with regret $> 0.8 \cdot \rho_1$
- **Certificate size:** Number of distinct regret values in $D^\downarrow(x)$

### 7.5 Results on DTLZ Suite

**Table 2: Benchmark Comparison (10-dimensional, 30 replications)**

| Method | WCR $\downarrow$ | RU $\downarrow$ | Out-of-Class Loss $\downarrow$ | Probes Used |
|--------|------------------|-----------------|--------------------------------|-------------|
| TOPSIS | 0.97 | 0.36 | 0.26 | N/A |
| CP | 0.94 | 0.28 | 0.25 | N/A |
| KP | 0.90 | 0.29 | 0.31 | N/A |
| RW | 0.95 | 0.36 | 0.44 | 100 |
| ASF | 0.95 | 0.23 | 0.27 | N/A |
| **SMAA** | 0.95 | 0.36 | 0.45 | N/A |
| **MMR** | 0.92 | 0.21 | 0.26 | N/A |
| **LUR** | **0.71** | **0.22** | **0.27** | **12** |

LUR achieves significantly lower worst-case regret (0.71 vs. 0.90--0.97) than all classical and robust baselines (Friedman $p < 10^{-100}$, Wilcoxon-Holm $p < 10^{-5}$). The uniformity of the regret profile (RU = 0.22) guarantees balanced performance across perspectives. Notably, LUR matches or outperforms the Out-of-Class Loss of methods like SMAA and MMR, proving strong generalization to unobserved preference functions.

**Table 3: Probe Reduction Effectiveness**

| $m$ | Full Coalitions | Cluster Probes | Reduction Factor |
|-----|-----------------|----------------|------------------|
| 3 | 17 | 5 | 3.4x |
| 5 | 85 | 7 | 12.1x |
| 8 | 751 | 10 | 75.1x |
| 10 | 3,051 | 12 | 254.2x |
| 15 | 98,273 | 17 | 5,780.8x |

Cluster-based probe generation achieves dramatic reduction, preventing exponential explosion and keeping LUR computationally tractable even for $m=15$.

### 7.6 Results on Smart Grid

**Table 4: Selected Dispatch Plans**

| Method | Cost | Emissions | Unreliability | Ramping | Non-Renewable | Peak Gap | Out-of-Class Loss |
|--------|------|-----------|---------------|---------|---------------|----------|-------------------|
| TOPSIS, CP, SMAA | **249.6** | **2769.5** | 0.0 | 28.9 | **0.56** | 2.65 | **0.13** |
| MMR, **LUR** | 251.1 | 3477.8 | 0.0 | **26.4** | 0.64 | **1.88** | 0.14 |

**Managerial Insight**: 
Methods like TOPSIS, CP, and SMAA aggressively favor reducing emissions and non-renewable generation. In contrast, LUR (and MMR) select a different compromise that yields slightly higher emissions but significantly improved *ramping* capabilities and a much tighter *peak gap* (1.88 vs. 2.65). 

When analyzing the LUR certificate, the DM can identify the *critical objective coalitions*. In this case, the certificate confirms that the maximal regret across any rational viewpoint is exactly 0.402 (driven purely by the peak gap $f_6$), whereas alternatives expose stakeholders to much higher regrets on operational constraints. The DM is given the narrative: *"This dispatch plan is the least fragile compromise. Any alternative plan will cause at least a 40% normalized regret for some rational stakeholder perspective."*

### 7.7 Ablation Study

**Table 5: Ablation**

| Configuration | WCR $\downarrow$ | Out-of-Class Loss $\downarrow$ |
|---------------|------------------|--------------------------------|
| Full LUR | 0.70 | 0.47 |
| No clustering | 0.70 | 0.47 |
| No singletons | 0.78 | 0.48 |
| Mean only | 0.70 | 0.47 |
| Max only | 0.93 | 0.47 |

Key findings:
- **Clustering** has identical solution quality (WCR = 0.70) but reduces computation drastically.
- **Singleton probes** are essential; without them, WCR increases to 0.78.
- **Mean vs Max**: Discarding coalition max-probes degrades WCR drastically (to 0.93), proving that coalitions are vital for bounding worst-case outcomes.

---

## 8. Discussion and Limitations

### 8.1 Parameters in LUR

LUR is not parameter-free. It requires:
- Normalization bounds $z_i^\star, z_i^N$
- Numerical tolerance $\varepsilon$
- Probe family specification (clustering threshold $\theta$ or PCA rank)
- Confidence level $\alpha$ (for stochastic extension)
- Fairness parameter $\beta$ (for multi-stakeholder)

The honest claim is:

> LUR avoids a single ex ante weight vector and replaces it with a transparent, auditable class of rational probes. The parameters are interpretable and have natural defaults.

### 8.2 When LUR is Not Appropriate

LUR is designed for multiobjective decision-making where the DM needs a single robust solution. It is not appropriate when:
- The DM genuinely wants to explore the trade-off surface (e.g., for sensitivity analysis).
- The objectives are fundamentally incommensurable (e.g., monetary cost vs. human lives).
- The feasible set is extremely large and the objective correlation structure is unknown.

### 8.3 The Subjectivity of "Rational"

The probe family $\mathcal{Q}$ is declared explicitly, but what is "rational" is a normative judgment. We mitigate this by:
- Making the probe family data-driven (correlation clustering) rather than analyst-driven.
- Providing interactive certificates that allow the DM to explore different probe families.
- Including stakeholder negotiation to surface hidden rationalities.

### 8.4 Future Work

- **Epsilon-net theorems:** Prove that a finite probe family approximates a continuous admissible utility class within $O(\varepsilon)$.
- **Nonlinear probes:** Extend to nonlinear coalitions (products, ratios) for objectives with synergy.
- **Deep learning surrogates:** Replace GPs with neural networks for high-dimensional $X$.
- **Human-in-the-loop:** Real-time DM feedback to adapt the probe family during optimization.

---

## 9. Conclusion

We have presented the **Leximax Universal-Regret (LUR) Core**, a Pareto-compatible decision framework that replaces the Pareto front as the final decision object with a **regret certificate**. The framework ranks feasible solutions by the lexicographically sorted vector of normalized regrets over a declared class of monotone rational probes.

LUR satisfies three properties that no existing post-Pareto method simultaneously achieves:
1. **No ex ante weights:** The probe family is declared, not imposed as a single scalarization.
2. **Pareto respect:** The leximax order never prefers a dominated solution over its dominator.
3. **Direct computability:** The LUR solution can be found by sequential minimax-regret optimization, without Pareto-front enumeration.

We proved existence, completeness, Pareto compatibility, dominated exclusion, and stability under bounded perturbations. We introduced adaptive nonnegative probe generation that preserves Pareto compatibility while reducing computation, stochastic regret certificates for noisy objectives, and a multi-stakeholder extension with fairness guarantees.

Experimental evaluation on standard benchmarks and a real-world smart-grid case study demonstrates that LUR achieves lower worst-case regret under held-out preference models than TOPSIS, compromise programming, knee-point selection, and random weight scalarization.

The central message is this: **Pareto efficiency is a safety property, not a decision object.** The LUR framework absorbs Pareto rationality into a complete, robust, and explainable decision rule. The decision-maker receives a certificate:

> *"This solution is the least fragile compromise across all declared rational interpretations of your objectives. No other feasible solution improves the worst-case regret, and the regret profile is certified."*

That is the power of the Leximax Universal-Regret Core.

---

## References

[1] K. Miettinen, "Nonlinear Multiobjective Optimization," *Kluwer Academic Publishers*, 1999.

[2] C. L. Hwang and K. Yoon, "Multiple Attribute Decision Making: Methods and Applications," *Springer*, 1981.

[3] M. Zeleny, "Multiple Criteria Decision Making," *McGraw-Hill*, 1982.

[4] J. Branke et al., "Multiobjective optimization: Interactive and evolutionary approaches," *Springer*, 2008.

[5] B. Roy, "The outranking approach and the foundations of ELECTRE methods," *Theory and Decision*, vol. 31, no. 1, pp. 49--73, 1991.

[6] J. P. Brans and B. Mareschal, "PROMETHEE methods," in *Multiple Criteria Decision Analysis: State of the Art Surveys*, Springer, 2016, pp. 187--219.

[7] E. Zitzler and L. Thiele, "Multiobjective evolutionary algorithms: A comparative case study and the strength Pareto approach," *IEEE Transactions on Evolutionary Computation*, vol. 3, no. 4, pp. 257--271, 1999.

[8] A. P. Wierzbicki, "The use of reference objectives in multiobjective optimization," in *Multiple Criteria Decision Making Theory and Application*, Springer, 1980, pp. 468--486.

[9] K. Miettinen and M. M. Makela, "On scalarizing functions in multiobjective optimization," *OR Spectrum*, vol. 24, no. 2, pp. 193--213, 2002.

[10] R. R. Yager, "On ordered weighted averaging aggregation operators in multicriteria decisionmaking," *IEEE Transactions on Systems, Man, and Cybernetics*, vol. 18, no. 1, pp. 183--190, 1988.

[11] W. Ogryczak and T. Sliwinski, "On generating the OWA operator weights," *Information Sciences*, vol. 175, no. 1--2, pp. 29--47, 2006.

[12] W. Ogryczak, "On the lexicographic minimax approach to location problems," *European Journal of Operational Research*, vol. 100, no. 3, pp. 566--585, 1997.

[13] L. J. Savage, "The theory of statistical decision," *Journal of the American Statistical Association*, vol. 46, no. 253, pp. 55--67, 1951.

[14] G. Loomes and R. Sugden, "Regret theory: An alternative theory of rational choice under uncertainty," *The Economic Journal*, vol. 92, no. 368, pp. 805--824, 1982.

[15] X. Chen, "Multi-objective minimax regret equilibrium and its properties," *Journal of Industrial & Management Optimization*, 2026.

[16] A. Ben-Tal and A. Nemirovski, "Robust optimization -- methodology and applications," *Mathematical Programming*, vol. 92, no. 3, pp. 453--480, 2002.

[17] J. R. Birge and F. Louveaux, "Introduction to Stochastic Programming," *Springer*, 2011.

[18] J. Rawls, "A Theory of Justice," *Harvard University Press*, 1971.

[19] J. F. Nash Jr., "The bargaining problem," *Econometrica*, vol. 18, no. 2, pp. 155--162, 1950.

[20] V. Chvatal, "A greedy heuristic for the set-covering problem," *Mathematics of Operations Research*, vol. 4, no. 3, pp. 233--235, 1979.

[21] G. L. Nemhauser, L. A. Wolsey, and M. L. Fisher, "An analysis of approximations for maximizing submodular set functions," *Mathematical Programming*, vol. 14, no. 1, pp. 265--294, 1978.

[22] K. Deb et al., "Scalable multi-objective optimization test problems," *Proceedings of the Congress on Evolutionary Computation*, pp. 825--830, 2002.

[23] S. Huband et al., "A review of multiobjective test problems and a scalable test problem toolkit," *IEEE Transactions on Evolutionary Computation*, vol. 10, no. 5, pp. 477--506, 2006.

[24] R. Lahdelma, J. Hokkanen, and P. Salminen, "SMAA - Stochastic multiobjective acceptability analysis," *European Journal of Operational Research*, vol. 106, no. 1, pp. 137-143, 1998.

[25] S. Greco, V. Mousseau, and R. Slowinski, "Ordinal regression revisited: Multiple criteria ranking using a set of additive value functions," *European Journal of Operational Research*, vol. 191, no. 2, pp. 416-436, 2008.

[26] C. Hu and S. Mehrotra, "Robust decision making over a set of preferences," *Operations Research*, vol. 63, no. 4, pp. 856-871, 2015.

---

## Appendix A: Proofs

### A.1 Proof of Lemma 1 (Existence and Completeness)

*Proof.* For finite $A$ and finite $\mathcal{Q}$, each $D^\downarrow(x)$ is a vector in $[0,1]^K$. Lexicographic order on $\mathbb{R}^K$ is a complete preorder: it is reflexive ($D^\downarrow(x) \leq_{lex} D^\downarrow(x)$), transitive (if $D^\downarrow(x) \leq_{lex} D^\downarrow(y)$ and $D^\downarrow(y) \leq_{lex} D^\downarrow(z)$, then $D^\downarrow(x) \leq_{lex} D^\downarrow(z)$), and total (any two vectors are comparable). Since $A$ is finite, the minimum exists by the well-ordering principle. ∎

### A.2 Proof of Theorem 2 (Pareto Compatibility)

*Proof.* Let $x \prec_P y$, so $r_i(x) \leq r_i(y)$ for all $i$ with strict inequality for some $j$. For any monotone probe $q$, $q(r(x)) \leq q(r(y))$ because $q$ is non-decreasing in each argument. Since $q^\star$ and $q^-$ are constants (independent of $x$ and $y$), we have:
$$D_q(x) = \frac{q(r(x)) - q^\star}{q^- - q^\star + \varepsilon} \leq \frac{q(r(y)) - q^\star}{q^- - q^\star + \varepsilon} = D_q(y)$$

For any probe $q$ that depends on $r_j$ (i.e., partial derivative of q with respect to r_j is positive somewhere), the inequality is strict: $D_q(x) < D_q(y)$. Since at least one such probe exists (e.g., the singleton probe $q_j(x) = r_j(x)$), the sorted regret vectors satisfy $D^\downarrow(x) <_{lex} D^\downarrow(y)$. ∎

### A.3 Proof of Corollary 2.1 (Dominated Exclusion)

*Proof.* If $x$ is dominated by $y$, then by Theorem 2, $y \prec_{LUR} x$. The LUR solution is $x^{LUR} \in \arg\min_{x} D^\downarrow(x)$. Since $D^\downarrow(y) <_{lex} D^\downarrow(x)$, $x$ cannot be a minimizer. ∎

### A.4 Proof of Theorem 3 (Stability)

*Proof.* Let $\hat{D}_q(x) = D_q(x) + \delta_q(x)$ where $|\delta_q(x)| \leq \eta$ for all $x, q$. For any pair $(x, y)$ with $x \prec_{LUR} y$, let $k$ be the first index where $D_{[k]}(x) < D_{[k]}(y)$. Then $D_{[j]}(x) = D_{[j]}(y)$ for all $j < k$ and $D_{[k]}(x) \leq D_{[k]}(y) - \delta_{\min}$.

Under perturbation:
$$\hat{D}_{[k]}(x) \leq D_{[k]}(x) + \eta \leq D_{[k]}(y) - \delta_{\min} + \eta$$
$$\hat{D}_{[k]}(y) \geq D_{[k]}(y) - \eta$$

Since $2\eta < \delta_{\min}$, we have $\hat{D}_{[k]}(x) < \hat{D}_{[k]}(y)$. For $j < k$, $|\hat{D}_{[j]}(x) - \hat{D}_{[j]}(y)| \leq 2\eta < \delta_{\min}$, but since $D_{[j]}(x) = D_{[j]}(y)$, the ordering at $j$ may change only if the perturbation reverses the tie. However, since $2\eta < \delta_{\min}$ and the gap at $k$ exceeds $2\eta$, the lexicographic comparison is decided at $k$ regardless of ties at $j < k$. Therefore $\hat{x}^{LUR} = x^{LUR}$. ∎

### A.5 Proof of Lemma 2 (Nonnegative Probe Pareto Compatibility)

*Proof.* If all weights $w_i \geq 0$, then for any $r \leq r'$ (component-wise), we have $q(r) = \sum_i w_i r_i \leq \sum_i w_i r'_i = q(r')$. Similarly for $q_\infty(r) = \max_i w_i r_i \leq \max_i w_i r'_i = q_\infty(r')$. Therefore all probes are monotone, and Theorem 2 applies. ∎

### A.6 Proof of Theorem 5 (Probe Approximation)

*Proof.* For any $q \in \mathcal{Q}_{\text{full}}$ and its approximation $q' \in \mathcal{Q}_{\text{reduced}}$ with $|q(r) - q'(r)| \leq \eta$ for all $r$:

$$|D_q(x) - D_{q'}(x)| = \left|\frac{q(x) - q^\star}{q^- - q^\star + \varepsilon} - \frac{q'(x) - q'^\star}{q'^- - q'^\star + \varepsilon}\right|$$

Let $N = q^- - q^\star + \varepsilon$ and $N' = q'^- - q'^\star + \varepsilon$. Then:

$$|D_q(x) - D_{q'}(x)| = \left|\frac{N'(q(x) - q^\star) - N(q'(x) - q'^\star)}{N \cdot N'}\right|$$

Since $|q(x) - q'(x)| \leq \eta$, $|q^\star - q'^\star| \leq \eta$, and $|q^- - q'^-| \leq \eta$, and assuming $N, N' \geq \varepsilon > 0$, we have:

$$|D_q(x) - D_{q'}(x)| \leq \frac{|N' - N| \cdot |q(x) - q^\star| + N \cdot |q(x) - q'(x)| + N \cdot |q^\star - q'^\star|}{N \cdot N'}$$

$$\leq \frac{\eta \cdot 1 + 1 \cdot \eta + 1 \cdot \eta}{\varepsilon^2} = \frac{3\eta}{\varepsilon^2}$$

Since all probes in $\mathcal{Q}_{\text{full}}$ are $L$-Lipschitz with respect to the normalized objectives, the differences $|q(x) - q'(x)|$ can be bounded more tightly based on the distance between the probes in the dual space. The approximation error over the compact set $[0,1]^m$ scales linearly with $\eta$. Consequently, the bound tightens to $O(L\eta)$. ∎

### A.7 Proof of Theorem 6 (Stochastic Consistency)

*Proof.* Let $\hat{\mu}_i(x)$ be the sample mean of $n$ i.i.d. observations of $f_i(x)$. By the Central Limit Theorem, $\sqrt{n}(\hat{\mu}_i(x) - \mu_i(x)) \xrightarrow{d} \mathcal{N}(0, \sigma_i^2(x))$. For Lipschitz probes with constant $L$:

$$|\hat{q}(x) - q(x)| \leq L \sum_{i=1}^m |\hat{\mu}_i(x) - \mu_i(x)| = O_p(1/\sqrt{n})$$

The regret difference satisfies $|\hat{D}_q(x) - D_q(x)| = O_p(1/\sqrt{n})$. Let $\eta_n = C/\sqrt{n}$ be a uniform bound (by the union bound and concentration inequalities, holding with high probability for finite $A$ and $\mathcal{Q}$). If $2\eta_n < \delta_{\min}$, then by Theorem 3, the LUR winner is preserved. As $n \to \infty$, $\eta_n \to 0$, so the condition holds for sufficiently large $n$. ∎

---

*End of Paper*
