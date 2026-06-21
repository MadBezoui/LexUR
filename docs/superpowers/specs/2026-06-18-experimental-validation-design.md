# Experimental Validation Enhancement Design

**Status:** Approved two-stage design

**Purpose:** Turn the current LexUR research package into a claim-driven,
reproducible validation program that can first support a defensible EJOR
submission and then support the full direct, stochastic, multi-stakeholder, and
real-application contribution.

## 1. Design Decision

The project will use two release gates.

1. **Stage 1, Defensible Core (4-6 weeks):** establish trustworthy provenance,
   correct the statistical design, validate the finite candidate-set rule and
   adaptive probes, characterize normalization failexure, and restrict manuscript
   claims to evidence that passes explicit gates.
2. **Stage 2, Full Contribution (8-12 additional weeks):** implement and validate
   exact direct LP/MILP LexUR, calibrated stochastic LexUR, non-tautological
   multi-stakeholder evaluation, and a real optimization case with external data.

Stage 2 does not block a Stage 1 submission. Stage 1 must label unfinished Stage
2 components as exploratory and must not use proxy experiments as proof.

## 2. Evidence Architecture

Every scientific claim is represented by a record containing:

- a stable claim identifier;
- the exact manuscript statement;
- the experiment and metric that could falsify it;
- a pre-specified acceptance threshold;
- the raw artifact and analysis artifact that constitute evidence;
- the current state: `supported`, `qualified`, `exploratory`, or `unsupported`.

Experiments write tidy, instance-level records. Aggregated CSV and JSON files are
derived artifacts, never the authoritative data. Each record includes the seed,
configuration hash, code commit, candidate size, criterion count, geometry,
replication, utility family, method, selected candidate, and metrics.

The pipeline has four layers:

1. `experiment`: generates immutable raw records;
2. `analysis`: computes stratified estimates and statistical models;
3. `gate`: evaluates pre-specified claim criteria without changing thresholds;
4. `report`: renders manuscript tables from gate-approved analysis artifacts.

## 3. Claim-to-Evidence Matrix

| ID | Contribution | Required evidence | Release gate |
|---|---|---|---|
| C1 | Finite-set LexUR is Pareto-compatible and invariant | Property tests plus dominated-injection and affine transformations | Zero dominated selections and 100% affine identity, with deterministic tie policy |
| C2 | LexUR has competitive tail robustness | Paired, stratified comparisons across geometry, dimension, size, utility family, and weight shape | Non-inferior to ASF and MMR under one frozen margin; multiplicity-controlled estimates and CIs reported |
| C3 | Adaptive probes approximate the full probe objective | Exact full-family comparison where tractable | Tail gap, worst-certificate gap, tolerance-set overlap, and runtime reported; no claim based only on average loss |
| C4 | Clustering reduces redundancy sensitivity | Known-group simulations across correlation/noise regimes | Improvement over unclustered LexUR and averaging baselines, with group-recovery uncertainty |
| C5 | LexUR is usable under estimated normalization bounds | Realistic bound-estimation and perturbation experiments | Quality and certificate stability remain inside declared limits, or method abstains/returns a stability set |
| C6 | LexUR can be computed directly on structured continuous problems | Exact sequential LP formulation compared with enumerated reference | Same lexicographic certificate within tolerance; scaling, solver calls, time, and failexures reported |
| C7 | LexUR can be computed directly on MILPs | Exact epigraph/lexicographic MILP, not a weighted-sum proxy | Exact agreement on small exhaustive cases and bounded-gap scaling results |
| C8 | Confidence-aware LexUR controls stochastic risk | Train/validation/test scenario design with criterion-specific risk | Calibrated coverage and out-of-sample CVaR/chance-risk comparison against stochastic baselines |
| C9 | Rawlsian LexUR improves stakeholder protection | Heterogeneous stakeholder models and metrics not identical to the optimized objective | Trade-off frontier for worst regret, welfare, inequality, and acceptability versus bargaining baselines |
| C10 | The certificate aids a real decision | Public optimization case and certificate evaluation | Reproducible physical model plus independent decision-quality or expert-usability evidence |

## 4. Stage 1 Scope

### 4.1 Evidence integrity

- Correct the 2,400/7,200 instance inconsistency and regenerate every protocol
  number directly from raw results.
- Replace “pre-registered” with “pre-specified/frozen” unless a verifiable public
  timestamp predates execution.
- Pin the Python environment and add a clean-environment smoke test.
- Add automated checks that manuscript constants match generated artifacts.

### 4.2 Statistical validity

- Preserve pairing within generated instances.
- Treat replication as nested within the crossed design factors rather than
  treating all 7,200 observations as exchangeable.
- Report factor-stratified effects and uncertainty, not only global ranks.
- Correct Holm adjustment and freeze one non-inferiority margin before rerunning.
- Use a hierarchical/bootstrap analysis at the problem-cell level.

### 4.3 Construct validity

- Split held-out utilities into in-class, adjacent, out-of-class, and adversarial
  groups. Do not claim that all utilities are unseen when baselines use related
  utility structures.
- Extend probe validation beyond mean tail loss to certificate approximation and
  tolerance-set stability.
- Make the failed nadir gate a central experiment. Add an instability diagnostic
  and an abstention/stability-set output if robust normalization cannot be shown.

### 4.4 Stage 1 manuscript policy

The smart-grid heuristic is described as a synthetic dispatch illustration. The
current four-solve facility-location proxy is removed as direct-MILP evidence.
Stochastic and stakeholder results remain exploratory. The main supported claim
is finite candidate-set selection with competitive tail quality, an auditable
certificate, and characterized redundancy/normalization behavior.

## 5. Stage 2 Scope

### 5.1 Direct optimization

Implement sequential epigraph solves. Each leximax stage fixes the preceding
ordered regret level within solver tolerance before optimizing the next. Small
LP and MILP cases are verified against complete feasible/candidate enumeration.
Scaling includes timeouts and failexures, not only successful averages.

### 5.2 Stochastic extension

Replace the raw-unit maximum threshold with declared criterion-specific loss and
risk functions. Use independent training, validation, and test scenarios, assess
confidence-bound calibration, and include distribution shift. Compare against
deterministic LexUR, stochastic ASF/MMR, SAA, and a distributionally robust method.

### 5.3 Multi-stakeholder extension

Generate linear and nonlinear stakeholder preferences, clustered disagreement,
and unequal importance. Evaluate worst regret, mean welfare, inequality, envy,
and epsilon-acceptability. Compare against utilitarian, Nash, Kalai-Smorodinsky,
max-min, and minimax-regret rules.

### 5.4 Real decision case

Use a public, recognized system and an actual constrained optimization model.
For a grid case, this means a documented IEEE system or equivalent public UC/ED
dataset, power balance, generator and ramp constraints, reproducible renewable
scenarios, and multiple operating conditions. The certificate is evaluated with
domain experts or a blinded decision task; a single favorable synthetic instance
does not validate decision-support value.

## 6. Acceptance Gates

### Stage 1 release gate

- Clean environment reproduces the smoke protocol.
- All generated tables trace to raw records and a configuration hash.
- Manuscript instance counts, ranks, confidence intervals, and gate states match
  generated artifacts automatically.
- Statistical tests pass unit tests and preserve pairing/block structure.
- C1-C4 are `supported` or explicitly `qualified`; C5 has a documented stability
  policy; C6-C10 are not described as fully validated.
- Negative and failed gates appear in the manuscript and generated report.

### Stage 2 release gate

- Exact direct solvers match exhaustive references on registered test suites.
- Stochastic risk metrics are unit-consistent and calibrated out of sample.
- Stakeholder conclusions hold on metrics not identical to the selection rule.
- The real case is externally sourced, physically constrained, and independently
  interpretable.
- C1-C10 each have direct evidence or are explicitly removed from the contribution.

## 7. Schedule and Dependencies

| Weeks | Work package | Depends on |
|---|---|---|
| 1 | Provenance, environment, tests, claim registry | None |
| 2 | Raw schema, corrected statistics, manuscript consistency | Week 1 |
| 3 | Probe and normalization validation | Week 2 |
| 4 | Stratified core rerun and analysis | Weeks 2-3 |
| 5 | Stage 1 manuscript rewrite and artifact audit | Week 4 |
| 6 | Buffer, independent reproduction, submission gate | Week 5 |
| 7-9 | Exact LP/MILP direct formulations | Stage 1 infrastructure |
| 8-10 | Calibrated stochastic and stakeholder studies | Stage 1 infrastructure |
| 9-13 | Public real case and expert/usability evaluation | Model/data access |
| 14-16 | Full rerun, synthesis, independent audit | All Stage 2 packages |

## 8. Resource Assumptions

- One primary researcher/engineer; statistical or OR review at Stage 1 and Stage
  2 gates.
- A solver with deterministic settings and recorded version; open-source solvers
  remain supported for reproduction.
- Compute budget is controlled by pilot/full configurations. No full rerun occurs
  until smoke and pilot gates pass.
- Expert/user validation requires ethics/consent review if human-subject rules at
  the host institution apply.

## 9. Risks and Responses

- **LexUR fails non-inferiority after corrected analysis:** narrow the empirical
  claim to certificate/robustness trade-offs and report conditions where it wins.
- **Normalization remains unstable:** return a tolerance/stability set, require
  bounds, or abstain; do not hide identity instability behind average quality.
- **Exact MILP does not scale:** retain the exact small-instance result and label
  large-scale methods as approximations with optimality gaps.
- **No expert access:** use a public benchmark and postpone usability claims; do
  not substitute author interpretation for independent validation.
- **Real case contradicts synthetic results:** report the contradiction and use it
  to define the method’s applicability conditions.

