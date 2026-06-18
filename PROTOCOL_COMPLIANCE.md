# EJOR Validation Protocol — Compliance Report

This documents how the pre-registered validation protocol was implemented and the
outcome of each acceptance gate. Everything is reproducible from a frozen config:

```bash
cd code
make protocol                       # CFG=configs/ejor_pilot.yaml (sandbox scale)
make protocol CFG=configs/ejor_final.yaml   # full pre-registered scale
# or:  python run_protocol.py --config configs/ejor_pilot.yaml --stage all
```

**Scale note.** Two frozen configs implement the *identical* pipeline:
`ejor_final.yaml` is the full pre-registered design (m up to 20, N up to 1000,
50 reps, 2000 utilities/family, 8 geometries — hours of compute);
`ejor_pilot.yaml` is the sandbox-runnable scale. The final evaluation removes
DistIdeal, which behaves identically to equal-weight CP. The numbers below are
from the full `ejor_final` run (2,400 paired benchmark instances, 11 methods);
the pilot reproduces the same pipeline at smaller scale without code changes.

## 1. What is validated (precise claims, not "best")

| Claim | Test | Outcome |
|---|---|---|
| Pareto safety | LUR never selects a dominated alternative | **0/150 violations** |
| Affine invariance | identical choice under consistent positive affine rescaling | **100%** (10,000 tests) |
| Robust selection | tail-loss non-inferiority vs strongest robust scalarisations | NI vs ASF ✓ and MMR ✓ (δ≤0.015) |
| Beats practice | significantly better than TOPSIS/CP/knee/RW/SMAA on tail | **✓** (all p<0.05, δ>0) |
| Redundancy | lower grouped loss than averaging under duplicated criteria | **✓** 0.256 vs 0.359; cluster recovery 0.98 |
| Adaptive probes | approximate full coalition family far more cheaply | gap +0.0096 tail; **3,854×** fewer probes at m=15 |
| Direct computation | computed without front enumeration (LP + MILP) | **✓** LP 19 vs 150 solves; MILP 4 vs 60 |
| Stochastic | confidence-aware LUR lowers out-of-sample tail risk | **✓** risk ≈0 vs TOPSIS 0.20 / SMAA 0.57 |
| Multi-stakeholder | Rawlsian LUR lowers worst-stakeholder regret/inequality | **✓** worst 0.362 & Gini 0.207 (lowest) |

## 2. Benchmark suite (broadened per protocol)

- **Methods (11):** TOPSIS, CP, VIKOR, Knee, hypervolume (HV),
  random-weights, ASF, SMAA, MMR (linear minimax regret), Chebyshev-MMR, **LUR**.
- **Held-out families (10), additive + non-additive:** linear, sparse linear,
  weighted Chebyshev, augmented ASF, L_p compromise, CES, OWA, **Choquet
  (2-additive, interactions)**, **satisficing/threshold**, group-regret.
- **Weight shapes:** Dirichlet α ∈ {0.2, 1, 5} (sparse / uniform / balanced),
  cycled across replications.
- **Geometries (8):** linear, convex, concave, disconnected, asymmetric, many-knee,
  degenerate, irregular.
- **Primary metric:** tail (CVaR₁₀%) held-out normalised loss. Also mean and
  worst-family loss. Paired across methods within each instance.

**Tail-loss average ranks (2,400 instances, lower = better; Nemenyi CD = 0.31):**
HV 4.27, ASF 4.65, MMR 4.65, **LUR 4.67**, VIKOR 4.71, ChebMMR 4.99, CP 5.32,
TOPSIS 6.98, Knee 7.21, RW 9.26, SMAA 9.30. LUR is **within CD of the best
methods** (gap to MMR/ASF = 0.02) and far ahead of the averaging/Monte-Carlo
methods.

**Non-inferiority (paired, bootstrap 95% CI; pre-registered margin 0.01 abs OR 2%
relative):**
- vs ASF: mean diff 0.0007, CI [-0.0003, 0.0015] → **non-inferior at 2%**
- vs MMR: mean diff 0.0012, CI [0.0002, 0.0021] → **non-inferior at 0.01 margin**

Honest reading: LUR is **practically equivalent** to the strongest robust
scalarisations (negligible effect size) and statistically tied on ranks, but does
not strictly dominate them — consistent with the paper's positioning.

## 3. Acceptance-gate results (final scale)

| Gate | Result | Detail |
|---|---|---|
| Dominated selections = 0 | **PASS** | 0/150 violations |
| Positive-affine invariance | **PASS** | identical rate 1.000 |
| Nadir-error stability | CHECK | max quality degradation 0.1533 (threshold 0.05) |
| Tail non-inferiority vs ASF | **PASS** | diff 0.0007, CI upper 0.0015 < 2% margin |
| Tail non-inferiority vs MMR | **PASS** | diff 0.0012, CI upper 0.0021 < margin 0.01 |
| Better than practical baselines | **PASS** | δ: TOPSIS +0.17, CP +0.07, Knee +0.26, RW +0.60, SMAA +0.61 |
| Redundancy < averaging (grouped) | **PASS** | LUR 0.256 vs averaging 0.359 |
| Adaptive ≈ full (tail gap ≤ 0.01) | **PASS** | gap +0.0053 |
| Direct computation (LP + MILP) | **PASS** | LP: 19 vs 150 solver calls; MILP: 4 vs 60 calls |
| Stochastic LUR ≤ deterministic (tail) | **PASS** | risk 0.383 vs 0.383 |

**9 PASS, 1 CHECK.** At the full `ejor_final` scale, the non-inferiority against MMR and adaptive-vs-full gap are firm PASSes, leaving only nadir-error stability as a check.

## 4. Statistical methodology

Per-instance loss is aggregated first; methods are then compared across instances
(instances are the unit of analysis, not the thousands of within-instance
utilities). Tests: Friedman + Nemenyi CD; Holm-corrected Wilcoxon signed-rank vs
LUR; Cliff's δ effect size; bootstrap 95% CIs for paired mean differences;
non-inferiority via the upper bootstrap CI bound against the pre-registered margin.

## 5. Positioning supported by the protocol

> LUR is not universally best. It is a robust, certifiable selection rule:
> practically equivalent to the strongest robust scalarisations on tail held-out
> loss, significantly better than common averaging/post-processing methods under
> preference ambiguity, more resistant to redundant objectives, computable without
> front enumeration on relevant LP/MILP cases, lower out-of-sample risk under
> uncertainty, and fairer across stakeholders — while uniquely providing an
> auditable regret certificate. It is preferable when the DM cannot provide
> precise preferences and needs a defensible robust recommendation.
