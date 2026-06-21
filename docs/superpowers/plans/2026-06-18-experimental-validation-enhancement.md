# Experimental Validation Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a submission-safe, claim-driven validation package first, then validate the full direct, stochastic, multi-stakeholder, and real-application LexUR contribution.

**Architecture:** Experiments emit immutable tidy records with provenance; analysis modules consume those records; claim gates evaluate frozen thresholds; manuscript tables are generated only from gate outputs. Work is split into a six-week defensible-core release and an additional eight-to-twelve-week full-contribution release.

**Tech Stack:** Python 3.11, NumPy, SciPy, pandas, scikit-learn, statsmodels, PyYAML, PuLP/CBC, pytest, LaTeX.

## Global Constraints

- Preserve seeded, paired comparisons across methods.
- Never overwrite or silently combine raw protocol chunks.
- Record code commit, configuration SHA-256, environment versions, and seed in every run manifest.
- Acceptance thresholds live in versioned YAML and cannot be inferred from results.
- Failed gates are rendered in reports and cannot be filtered out.
- Pilot gates must pass before any compute-heavy full run.
- Treat the current smart-grid model, stochastic metric, stakeholder study, and facility-location direct proxy as exploratory until their replacement tasks pass.
- Do not claim public preregistration without an external timestamp that predates execution.

---

## Stage 1: Defensible Core

### Task 1: Reproducible Environment and Test Harness

**Files:**
- Create: `code/pyproject.toml`
- Create: `code/requirements-dev.txt`
- Create: `code/tests/test_smoke.py`
- Modify: `code/requirements.txt`
- Modify: `code/Makefile`
- Modify: `README.md`

**Interfaces:**
- Consumes: existing `lexur` package and `_smoke.yaml`.
- Produces: `make test`, `make smoke`, and a documented Python 3.11 environment.

- [ ] **Step 1: Add a failing import and deterministic-selection test**

```python
# code/tests/test_smoke.py
import numpy as np

from lexur import methods, problems


def test_seeded_candidate_selection_is_deterministic():
    f1 = problems.make_candidate_set("concave", 40, 4, np.random.default_rng(19))
    f2 = problems.make_candidate_set("concave", 40, 4, np.random.default_rng(19))
    assert np.array_equal(f1, f2)
    assert methods.lexur(f1) == methods.lexur(f2)
```

- [ ] **Step 2: Run the isolated test and confirm the unconfigured harness fails**

Run: `cd code && python -m pytest tests/test_smoke.py -v`

Expected: pytest is unavailable or project metadata is missing from a clean environment.

- [ ] **Step 3: Add package and test metadata**

```toml
# code/pyproject.toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "lexur"
version = "0.1.0"
requires-python = ">=3.11,<3.12"
dependencies = [
  "numpy>=1.26,<2.0",
  "scipy>=1.11,<1.14",
  "pandas>=2.1,<2.3",
  "scikit-learn>=1.3,<1.6",
  "matplotlib>=3.8,<3.10",
  "PyYAML>=6.0,<7",
  "PuLP>=2.8,<3",
  "statsmodels>=0.14,<0.15",
]

[tool.setuptools.packages.find]
where = ["."]
include = ["lexur*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

```text
# code/requirements-dev.txt
-e .
pytest>=8.2,<9
pytest-cov>=5,<6
```

- [ ] **Step 4: Add Make targets**

```make
test:
	python -m pytest -q

smoke:
	python run_protocol.py --config configs/_smoke.yaml --stage all
```

- [ ] **Step 5: Verify in a clean virtual environment**

Run: `cd code && python3.11 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && .venv/bin/python -m pytest -q`

Expected: `1 passed` with no NumPy ABI warning.

- [ ] **Step 6: Commit the environment gate**

```bash
git add code/pyproject.toml code/requirements.txt code/requirements-dev.txt code/tests/test_smoke.py code/Makefile README.md
git commit -m "test: establish reproducible validation environment"
```

### Task 2: Claim Registry and Provenance Manifest

**Files:**
- Create: `code/configs/claims.yaml`
- Create: `code/lexur/provenance.py`
- Create: `code/tests/test_provenance.py`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Consumes: parsed experiment config and repository root.
- Produces: `build_manifest(config_path: str, seed: int) -> dict` and `results/protocol/run_manifest.json`.

- [ ] **Step 1: Write failing manifest tests**

```python
# code/tests/test_provenance.py
import json
from pathlib import Path

from lexur.provenance import build_manifest, sha256_file


def test_manifest_contains_reproducibility_fields(tmp_path: Path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("seed: 17\n", encoding="utf-8")
    manifest = build_manifest(str(cfg), seed=17)
    assert manifest["seed"] == 17
    assert manifest["config_sha256"] == sha256_file(cfg)
    assert manifest["python"]
    assert manifest["packages"]["numpy"]
    assert "git_commit" in manifest


def test_manifest_round_trip(tmp_path: Path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("seed: 17\n", encoding="utf-8")
    payload = build_manifest(str(cfg), seed=17)
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    assert json.loads(path.read_text())["config_sha256"] == payload["config_sha256"]
```

- [ ] **Step 2: Verify the tests fail because the provenance module does not exist**

Run: `cd code && python -m pytest tests/test_provenance.py -v`

Expected: `ModuleNotFoundError: No module named 'lexur.provenance'`.

- [ ] **Step 3: Implement the manifest**

```python
# code/lexur/provenance.py
from __future__ import annotations

import hashlib
import importlib.metadata
import platform
import subprocess
from pathlib import Path


PACKAGES = ("numpy", "scipy", "pandas", "scikit-learn", "matplotlib", "PyYAML", "PuLP", "statsmodels")


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git_commit(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=cwd, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
    )
    return result.stdout.strip() or None


def build_manifest(config_path: str, seed: int) -> dict:
    root = Path(config_path).resolve().parents[2]
    versions = {}
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {
        "seed": int(seed),
        "config_path": str(Path(config_path).resolve()),
        "config_sha256": sha256_file(config_path),
        "git_commit": _git_commit(root),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": versions,
    }
```

- [ ] **Step 4: Create the initial claim registry**

```yaml
# code/configs/claims.yaml
claims:
  C1:
    statement: finite-set LexUR excludes dominated alternatives and is positive-affine invariant
    stage: core
    gates: [dominated_injection, affine_invariance]
  C2:
    statement: LexUR is non-inferior to ASF and MMR on tail held-out loss
    stage: core
    gates: [tail_noninferiority_asf, tail_noninferiority_mmr]
  C3:
    statement: adaptive probes approximate the full probe objective where tractable
    stage: core
    gates: [probe_tail_gap, probe_certificate_gap, probe_tolerance_overlap]
  C4:
    statement: correlation-aware probes reduce redundancy sensitivity
    stage: core
    gates: [redundancy_grouped_loss, cluster_recovery]
  C5:
    statement: LexUR reports instability when normalization bounds are unreliable
    stage: core
    gates: [normalization_quality, normalization_certificate, normalization_abstention]
  C6: {statement: exact direct LP LexUR matches exhaustive reference, stage: extension, gates: [direct_lp_exactness]}
  C7: {statement: exact direct MILP LexUR matches exhaustive reference, stage: extension, gates: [direct_milp_exactness]}
  C8: {statement: stochastic LexUR controls calibrated out-of-sample risk, stage: extension, gates: [stochastic_calibration]}
  C9: {statement: Rawlsian LexUR protects stakeholders across independent metrics, stage: extension, gates: [stakeholder_tradeoff]}
  C10: {statement: the certificate aids a real decision, stage: extension, gates: [real_case_reproducibility, certificate_utility]}
```

- [ ] **Step 5: Write the manifest at protocol startup and refuse accidental overwrite**

Modify `run_protocol.py` to call `build_manifest`, compare an existing manifest’s
configuration hash, and exit unless `--new-run-id` is supplied when hashes differ.

- [ ] **Step 6: Run provenance and smoke tests**

Run: `cd code && python -m pytest tests/test_provenance.py tests/test_smoke.py -v`

Expected: all tests pass and `run_manifest.json` contains the current commit and config hash.

- [ ] **Step 7: Commit the evidence contract**

```bash
git add code/configs/claims.yaml code/lexur/provenance.py code/tests/test_provenance.py code/run_protocol.py
git commit -m "feat: register claims and experiment provenance"
```

### Task 3: Tidy Raw Results and Exact Protocol Accounting

**Files:**
- Create: `code/lexur/records.py`
- Create: `code/tests/test_records.py`
- Modify: `code/run_protocol.py`
- Modify: `code/configs/ejor_final.yaml`

**Interfaces:**
- Produces: `BenchmarkRecord` and `results/protocol/raw/benchmark.parquet`.
- Required columns: `run_id`, `config_sha256`, `seed`, `N`, `m`, `geometry`, `replication`, `dirichlet_alpha`, `method`, `utility_scope`, `mean_loss`, `tail_loss`, `worst_family`, `selected_index`.

- [ ] **Step 1: Write schema and expected-count tests**

```python
# code/tests/test_records.py
from lexur.records import expected_benchmark_cells, validate_benchmark_frame


def test_expected_full_protocol_count():
    cfg = {
        "candidate_sizes": [100, 300, 1000],
        "criteria": [3, 5, 8, 10, 15, 20],
        "geometries": ["a", "b", "c", "d", "e", "f", "g", "h"],
        "replications": 50,
    }
    assert expected_benchmark_cells(cfg) == 7200
```

- [ ] **Step 2: Verify the count test fails**

Run: `cd code && python -m pytest tests/test_records.py -v`

Expected: missing `lexur.records`.

- [ ] **Step 3: Implement schema validation and expected counts**

```python
# code/lexur/records.py
REQUIRED_BENCHMARK_COLUMNS = {
    "run_id", "config_sha256", "seed", "N", "m", "geometry",
    "replication", "dirichlet_alpha", "method", "utility_scope",
    "mean_loss", "tail_loss", "worst_family", "selected_index",
}


def expected_benchmark_cells(cfg: dict) -> int:
    return (
        len(cfg["candidate_sizes"])
        * len(cfg["criteria"])
        * len(cfg["geometries"])
        * int(cfg["replications"])
    )


def validate_benchmark_frame(frame, cfg: dict) -> None:
    missing = REQUIRED_BENCHMARK_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"missing benchmark columns: {sorted(missing)}")
    cells = frame[["N", "m", "geometry", "replication"]].drop_duplicates()
    expected = expected_benchmark_cells(cfg)
    if len(cells) != expected:
        raise ValueError(f"expected {expected} benchmark cells, found {len(cells)}")
```

- [ ] **Step 4: Refactor benchmark chunks to preserve factor labels**

Each `_bench_block` iteration must append one record per method with its exact
factor values. Chunk finalization must reject duplicated factor-method keys and
missing cells before creating aggregate outputs.

- [ ] **Step 5: Separate evaluation scopes**

Add `utility_scope` values `in_class`, `adjacent`, `out_of_class`, and
`adversarial` to the family configuration and raw records. Do not describe all
families collectively as unseen.

- [ ] **Step 6: Run the smoke protocol and inspect accounting**

Run: `cd code && python run_protocol.py --config configs/_smoke.yaml --stage benchmark`

Expected: raw records pass schema validation and printed expected/observed cell counts match.

- [ ] **Step 7: Commit raw-data accounting**

```bash
git add code/lexur/records.py code/tests/test_records.py code/run_protocol.py code/configs/ejor_final.yaml
git commit -m "feat: preserve tidy benchmark records and factor accounting"
```

### Task 4: Correct Statistical Inference

**Files:**
- Create: `code/lexur/analysis.py`
- Create: `code/tests/test_stats.py`
- Modify: `code/lexur/stats.py`
- Modify: `code/lexur/gates.py`
- Modify: `code/configs/ejor_final.yaml`

**Interfaces:**
- Produces: `holm_adjust(pvalues)`, `cluster_bootstrap_difference(frame, control, treatment, cluster_columns, seed)`, and stratified effect tables.

- [ ] **Step 1: Add known-value Holm tests**

```python
# code/tests/test_stats.py
import numpy as np
from lexur.stats import holm_adjust


def test_holm_adjust_is_monotone_in_sorted_order():
    raw = np.array([0.01, 0.04, 0.03])
    adjusted = holm_adjust(raw)
    assert np.allclose(adjusted, [0.03, 0.06, 0.06])


def test_holm_adjust_caps_at_one():
    assert np.all(holm_adjust(np.array([0.6, 0.8])) <= 1.0)
```

- [ ] **Step 2: Confirm the test fails against the existing implementation**

Run: `cd code && python -m pytest tests/test_stats.py -v`

Expected: `holm_adjust` is absent.

- [ ] **Step 3: Implement monotone Holm adjustment**

```python
def holm_adjust(pvalues):
    p = np.asarray(pvalues, dtype=float)
    order = np.argsort(p)
    scaled = (len(p) - np.arange(len(p))) * p[order]
    monotone = np.minimum(1.0, np.maximum.accumulate(scaled))
    out = np.empty_like(monotone)
    out[order] = monotone
    return out
```

- [ ] **Step 4: Replace observation-level bootstrap with cell-cluster bootstrap**

Use `(N, m, geometry, replication)` as the paired resampling unit. Preserve all
method rows in a sampled cell. Produce mean difference, percentile CI, and the
fraction of strata in which the conclusion reverses.

- [ ] **Step 5: Freeze one non-inferiority rule**

In `ejor_final.yaml`, replace the current absolute-or-relative behavior with:

```yaml
noninferiority:
  metric: tail_loss
  margin_absolute: 0.01
  confidence: 0.95
  controls: [ASF, MMR]
  bootstrap_unit: [N, m, geometry, replication]
  bootstrap_repetitions: 10000
```

- [ ] **Step 6: Add stratified analysis outputs**

Write `benchmark_by_geometry.csv`, `benchmark_by_dimension.csv`,
`benchmark_by_size.csv`, and `benchmark_by_utility_scope.csv`, each with effect,
CI, sample-cell count, and reversal indicator.

- [ ] **Step 7: Verify tests and pilot analysis**

Run: `cd code && python -m pytest tests/test_stats.py -v && python run_protocol.py --config configs/ejor_pilot.yaml --stage benchmark`

Expected: Holm tests pass; pilot report includes global and stratified uncertainty.

- [ ] **Step 8: Commit corrected inference**

```bash
git add code/lexur/analysis.py code/lexur/stats.py code/lexur/gates.py code/tests/test_stats.py code/configs/ejor_final.yaml
git commit -m "fix: use blocked inference and correct Holm adjustment"
```

### Task 5: Adaptive Probe Approximation Study

**Files:**
- Create: `code/lexur/probe_validation.py`
- Create: `code/tests/test_probe_validation.py`
- Modify: `code/lexur/methods.py`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Produces: `compare_probe_families(F, tolerance, theta) -> dict` containing winner agreement, tolerance-set Jaccard overlap, worst-regret gap, certificate sup-norm gap, probe counts, and runtime.

- [ ] **Step 1: Add a test where adaptive and full probes are identical**

```python
# code/tests/test_probe_validation.py
import numpy as np
from lexur.probe_validation import compare_probe_families


def test_two_criterion_complete_adaptive_family_has_zero_regret_gap():
    F = np.array([[0.0, 1.0], [0.4, 0.4], [1.0, 0.0]])
    result = compare_probe_families(F, tolerance=1e-9, theta=0.6)
    assert result["worst_regret_gap"] <= 1e-9
    assert 0.0 <= result["tolerance_jaccard"] <= 1.0
```

- [ ] **Step 2: Expose probe details for every LexUR variant**

Add `lexur_variant(..., return_detail=True)` returning selected index,
disappointment matrix, labels, and probes, matching `lexur`.

- [ ] **Step 3: Implement decision-set and certificate comparisons**

Define the tolerance set as all candidates whose sorted certificate is
lexicographically indistinguishable under the declared component tolerance.
Align common probe labels for certificate gaps and separately report omitted
full-family probes.

- [ ] **Step 4: Run factorial probe validation**

Use `m={2,3,4,5,6,8}`, all geometries, 50 replications, theta values
`{0.3,0.5,0.6,0.7,0.9}`, and record runtime/probe count. Full probes are required
only where the configured memory estimate is below 2 GB.

- [ ] **Step 5: Replace the misleading adaptive gate**

The gate must not pass on average tail gap alone. It reports separate statuses for
predictive quality, certificate approximation, and decision-set agreement.

- [ ] **Step 6: Verify and commit**

Run: `cd code && python -m pytest tests/test_probe_validation.py -v && python run_protocol.py --config configs/ejor_pilot.yaml --stage probes`

```bash
git add code/lexur/probe_validation.py code/tests/test_probe_validation.py code/lexur/methods.py code/run_protocol.py
git commit -m "feat: validate adaptive probes against full certificates"
```

### Task 6: Normalization Stability and Abstention

**Files:**
- Create: `code/lexur/normalization.py`
- Create: `code/tests/test_normalization.py`
- Modify: `code/lexur/methods.py`
- Modify: `code/lexur/gates.py`
- Modify: `code/configs/ejor_final.yaml`

**Interfaces:**
- Produces: `normalization_stability(F, bound_samples, tolerance) -> StabilityResult` and `lexur_stable(...) -> recommendation | stability set | abstention`.

- [ ] **Step 1: Write invariant and instability tests**

```python
# code/tests/test_normalization.py
import numpy as np
from lexur.normalization import lexur_stable


def test_stable_result_returns_single_recommendation():
    F = np.array([[0.0, 1.0], [0.5, 0.5], [1.0, 0.0]])
    bounds = [(F.min(0), F.max(0))] * 10
    result = lexur_stable(F, bounds, min_identity_rate=0.9, max_set_size=2)
    assert result.status == "recommend"
    assert len(result.indices) == 1


def test_unstable_result_does_not_claim_unique_recommendation():
    F = np.array([[0.0, 0.9], [0.4, 0.4], [0.9, 0.0]])
    bounds = [
        (np.zeros(2), np.array([1.0, 1.0])),
        (np.zeros(2), np.array([1.0, 3.0])),
    ]
    result = lexur_stable(F, bounds, min_identity_rate=0.9, max_set_size=1)
    assert result.status in {"set", "abstain"}
```

- [ ] **Step 2: Implement robust result types and stability policy**

Use a frozen policy: recommend when one index is selected in at least 90% of
bound samples; return a stability set when at most three candidates cover 95%;
otherwise abstain.

- [ ] **Step 3: Add realistic bound estimators**

Compare observed min/max, 1%-99% quantiles, bounds estimated from incomplete
candidate subsets, and domain-provided intervals. Generate asymmetric and
correlated bound errors.

- [ ] **Step 4: Record four stability outcomes**

For every error regime report identity rate, tolerance-set overlap, held-out
quality degradation, and certificate sup-norm change. Retain the existing failed
nadir gate in the output for historical comparison.

- [ ] **Step 5: Verify and commit**

Run: `cd code && python -m pytest tests/test_normalization.py -v && python run_protocol.py --config configs/ejor_pilot.yaml --stage gates`

```bash
git add code/lexur/normalization.py code/tests/test_normalization.py code/lexur/methods.py code/lexur/gates.py code/configs/ejor_final.yaml
git commit -m "feat: expose normalization stability and abstention"
```

### Task 7: Stage 1 Claim Gate and Manuscript Synchronization

**Files:**
- Create: `code/lexur/claim_gate.py`
- Create: `code/scripts/check_manuscript_numbers.py`
- Create: `code/tests/test_claim_gate.py`
- Modify: `code/run_protocol.py`
- Modify: `paper/sections/07_experiments.tex`
- Modify: `paper/sections/08_discussion.tex`
- Modify: `paper/sections/09_conclusion.tex`
- Modify: `paper/sections/B_smartgrid.tex`
- Modify: `PROTOCOL_COMPLIANCE.md`

**Interfaces:**
- Produces: `results/protocol/claim_status.json`, generated LaTeX macros in `paper/generated/protocol_numbers.tex`, and a nonzero exit status for manuscript drift.

- [ ] **Step 1: Write a failing claim-state test**

```python
# code/tests/test_claim_gate.py
from lexur.claim_gate import summarize_claim


def test_failed_required_gate_prevents_supported_status():
    claim = {"stage": "core", "gates": ["a", "b"]}
    gates = {"a": {"result": "PASS"}, "b": {"result": "CHECK"}}
    assert summarize_claim(claim, gates) == "qualified"
```

- [ ] **Step 2: Implement claim status as a pure function**

Rules: all required gates pass gives `supported`; any `CHECK` gives `qualified`;
missing extension evidence gives `exploratory`; a failed falsification threshold
gives `unsupported`.

- [ ] **Step 3: Generate manuscript constants**

Create LaTeX macros for instance count, method count, CD, ranks,
non-inferiority CIs, and gate counts. Replace hard-coded protocol values in the
paper with these macros.

- [ ] **Step 4: Correct current scope statements**

State 7,200 instances for the current full configuration, call the protocol
“frozen” rather than publicly preregistered, describe the current grid experiment
as a ten-generator heuristic illustration, and remove the facility-location proxy
from direct-MILP proof.

- [ ] **Step 5: Add a manuscript drift command**

Run: `cd code && python scripts/check_manuscript_numbers.py ../paper/main.tex ../results/protocol`

Expected: exit `0`; changing any generated count in a test fixture makes it exit `1`.

- [ ] **Step 6: Run the complete Stage 1 pilot gate**

Run: `cd code && python -m pytest -q && python run_protocol.py --config configs/ejor_pilot.yaml --stage all && python scripts/check_manuscript_numbers.py ../paper/main.tex ../results/protocol`

Expected: tests pass; every C1-C5 status is present; C6-C10 are exploratory; failed gates remain visible.

- [ ] **Step 7: Commit Stage 1 integration**

```bash
git add code/lexur/claim_gate.py code/scripts/check_manuscript_numbers.py code/tests/test_claim_gate.py code/run_protocol.py paper/sections PROTOCOL_COMPLIANCE.md
git commit -m "docs: synchronize manuscript claims with validation gates"
```

### Task 8: Full Core Rerun and Independent Audit

**Files:**
- Modify: `code/configs/ejor_final.yaml`
- Create: `results/protocol/audit/stage1_audit.md`

**Interfaces:**
- Consumes: all Stage 1 code and frozen full config.
- Produces: immutable run directory, audit report, and Stage 1 go/no-go decision.

- [ ] **Step 1: Tag the final config hash in the audit record**

Run: `cd code && shasum -a 256 configs/ejor_final.yaml`

Expected: record the hash before any full computation.

- [ ] **Step 2: Execute benchmark chunks without changing configuration**

Run the existing chunk mechanism for each candidate-size/dimension group, then
finalize only after schema validation proves exactly 7,200 unique problem cells.

- [ ] **Step 3: Run all non-benchmark stages**

Run: `cd code && python run_protocol.py --config configs/ejor_final.yaml --stage redundancy && python run_protocol.py --config configs/ejor_final.yaml --stage probes && python run_protocol.py --config configs/ejor_final.yaml --stage gates`

Expected: raw artifacts, stratified analysis, and claim status are generated from the same config hash.

- [ ] **Step 4: Audit one result manually**

Select one stored problem cell, recompute every method’s selected index and loss
from its seed/config, and record exact equality or numerical tolerance in
`stage1_audit.md`.

- [ ] **Step 5: Build and inspect the paper**

Run: `cd paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex`

Expected: successful build with no undefined references; all protocol numbers come from generated macros.

- [ ] **Step 6: Apply the Stage 1 decision rule**

Proceed to submission preparation only if the clean-environment, provenance,
accounting, statistics, C1-C5 status, manuscript-drift, and paper-build checks all
pass. Otherwise record a no-go with the failed claim identifiers.

- [ ] **Step 7: Commit the audit, not bulky regenerated intermediates unless repository policy requires them**

```bash
git add code/configs/ejor_final.yaml results/protocol/audit/stage1_audit.md
git commit -m "research: record stage one validation audit"
```

---

## Stage 2: Full Contribution

### Task 9: Exact Direct LP LexUR

**Files:**
- Create: `code/lexur/direct_lp.py`
- Create: `code/tests/test_direct_lp.py`
- Modify: `code/lexur/directopt.py`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Produces: `solve_direct_lp(problem, probes, lex_tolerance) -> DirectResult` with decision, sorted regret levels, solver status, calls, and runtime.

- [ ] **Step 1: Write an exhaustive-reference test**

Construct a two-variable bounded LP whose vertices can be enumerated. Assert that
direct and vertex-enumerated LexUR have identical sorted certificate vectors within
`1e-7`.

- [ ] **Step 2: Implement anchor solves and first epigraph stage**

For each linear probe compute best/worst anchors exactly, then minimize `rho` with
all normalized-regret constraints.

- [ ] **Step 3: Implement sequential leximax stages**

After each stage, identify active regrets within `lex_tolerance`, fix the achieved
level, and optimize the next distinct regret level until all probes are ordered.

- [ ] **Step 4: Verify against 100 random small LPs**

Run: `cd code && python -m pytest tests/test_direct_lp.py -v`

Expected: all certificate comparisons pass; failexures include serialized problem data.

- [ ] **Step 5: Add scaling experiment**

Use variables `{10,50,100,500}`, constraints `{10,50,200}`, objectives
`{3,5,8,10}`, and report median/IQR time, calls, memory, failexures, and quality.

- [ ] **Step 6: Commit exact LP support**

```bash
git add code/lexur/direct_lp.py code/tests/test_direct_lp.py code/lexur/directopt.py code/run_protocol.py
git commit -m "feat: solve exact direct LP LexUR lexicographically"
```

### Task 10: Exact Direct MILP LexUR

**Files:**
- Create: `code/lexur/direct_milp.py`
- Create: `code/tests/test_direct_milp.py`
- Modify: `code/lexur/directopt.py`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Produces: `solve_direct_milp(model_factory, probes, lex_tolerance, time_limit) -> DirectResult`.

- [ ] **Step 1: Replace the four-weight proxy test with exhaustive binary cases**

For facility-location instances with at most five facilities, enumerate all
feasible opening sets and assignments, compute exact finite LexUR, and compare the
MILP decision/certificate.

- [ ] **Step 2: Build the epigraph MILP**

Create normalized regret expressions from exact anchor solves, introduce stage
epigraph variables, and preserve integrality in every sequential solve.

- [ ] **Step 3: Record optimality evidence**

Return solver status, incumbent, best bound, relative gap, nodes, calls, and time.
Never label a time-limited incumbent as exact.

- [ ] **Step 4: Run exactness tests under CBC**

Run: `cd code && python -m pytest tests/test_direct_milp.py -v`

Expected: exhaustive small cases agree exactly; unavailable solver causes an explicit skip, not a pass.

- [ ] **Step 5: Run scaling with transparent timeouts**

Use facilities `{5,8,12,20}`, customers `{10,25,50}`, objectives `{3,5}`, 30
replications, and fixed 600-second limit. Report success and timeout rates.

- [ ] **Step 6: Commit exact MILP support**

```bash
git add code/lexur/direct_milp.py code/tests/test_direct_milp.py code/lexur/directopt.py code/run_protocol.py
git commit -m "feat: replace direct MILP proxy with exact formulation"
```

### Task 11: Calibrated Stochastic LexUR

**Files:**
- Create: `code/lexur/stochastic.py`
- Create: `code/tests/test_stochastic.py`
- Modify: `code/lexur/extras_validation.py`
- Modify: `code/configs/ejor_final.yaml`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Produces: criterion-specific `RiskSpecification`, `fit_stochastic_lexur`, and `evaluate_out_of_sample`.

- [ ] **Step 1: Add unit-consistency tests**

Assert that positive affine rescaling of one criterion and its threshold leaves
chance-violation probabilities unchanged. Assert that independent test scenarios
are not reused in fitting.

- [ ] **Step 2: Define explicit risk measures**

Support expected criterion value, upper quantile, CVaR, and chance violation per
criterion. Reject a single raw threshold applied across heterogeneous criteria.

- [ ] **Step 3: Split scenario roles**

Use independent train/validation/test seeds. Tune confidence level only on
validation scenarios and report once on at least 10,000 independent test scenarios.

- [ ] **Step 4: Add calibration and shift regimes**

Evaluate nominal Gaussian noise, heavy tails, correlated criteria, variance
misspecification, and mean/variance distribution shift. Report empirical coverage
against nominal confidence.

- [ ] **Step 5: Add stochastic comparators**

Compare deterministic LexUR, stochastic LexUR, stochastic ASF, stochastic MMR, SAA,
and a distributionally robust baseline under shared scenarios.

- [ ] **Step 6: Verify and commit**

Run: `cd code && python -m pytest tests/test_stochastic.py -v && python run_protocol.py --config configs/ejor_pilot.yaml --stage stochastic`

```bash
git add code/lexur/stochastic.py code/tests/test_stochastic.py code/lexur/extras_validation.py code/configs/ejor_final.yaml code/run_protocol.py
git commit -m "feat: validate stochastic LexUR with calibrated risk"
```

### Task 12: Independent Multi-Stakeholder Evaluation

**Files:**
- Create: `code/lexur/stakeholders.py`
- Create: `code/tests/test_stakeholders.py`
- Modify: `code/lexur/extras_validation.py`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Produces: stakeholder generators, selection baselines, and metric table independent of the optimized rule.

- [ ] **Step 1: Add metric sanity tests**

Verify that identical stakeholder outcomes have zero Gini/envy and that Pareto
domination across every stakeholder is detected.

- [ ] **Step 2: Generate heterogeneous stakeholder populations**

Include linear, Chebyshev, satisficing, and OWA preferences; clustered conflict;
minority blocs; and unequal declared importance.

- [ ] **Step 3: Implement comparison rules**

Include utilitarian, Nash bargaining, Kalai-Smorodinsky, max-min, minimax regret,
and Rawls-LexUR with deterministic tie handling.

- [ ] **Step 4: Evaluate independent outcomes**

Report worst regret, mean welfare, lower-decile welfare, Gini, envy rate,
Pareto-efficiency rate, and epsilon-acceptability. Present trade-off frontiers
rather than declaring one universal winner.

- [ ] **Step 5: Verify and commit**

Run: `cd code && python -m pytest tests/test_stakeholders.py -v && python run_protocol.py --config configs/ejor_pilot.yaml --stage multistakeholder`

```bash
git add code/lexur/stakeholders.py code/tests/test_stakeholders.py code/lexur/extras_validation.py code/run_protocol.py
git commit -m "feat: evaluate stakeholder tradeoffs independently"
```

### Task 13: Public Real Optimization Case

**Files:**
- Create: `code/lexur/cases/grid/model.py`
- Create: `code/lexur/cases/grid/data.py`
- Create: `code/lexur/cases/grid/scenarios.py`
- Create: `code/lexur/cases/grid/evaluate.py`
- Create: `code/tests/test_grid_case.py`
- Create: `data/grid/README.md`
- Modify: `code/lexur/smartgrid.py`
- Modify: `paper/sections/B_smartgrid.tex`

**Interfaces:**
- Produces: a documented UC/ED model, public-data checksum manifest, feasible schedules, objective records, and certificate report.

- [ ] **Step 1: Select and freeze one public benchmark**

Record source URL, license, exact files, checksums, bus/generator counts, base MVA,
and any transformations in `data/grid/README.md`. If redistribution is forbidden,
provide a verified fetch script and checksum instead of committing the data.

- [ ] **Step 2: Add physical-model tests**

Test hourly power balance, generator bounds, ramp limits, renewable availability,
storage energy conservation if included, and objective-unit calculations on a
three-bus fixture.

- [ ] **Step 3: Implement the optimization model**

Separate data loading, scenario generation, constrained model construction, and
evaluation. Do not generate “dispatch” solely from a preference vector.

- [ ] **Step 4: Validate against a known operating point**

Reproduce a published or benchmark reference cost/feasibility result within a
declared tolerance before running multicriteria experiments.

- [ ] **Step 5: Run multiple operating regimes**

Use at least 30 days/regimes spanning load and renewable conditions, independent
test scenarios, and the same paired selection methods as the core benchmark.

- [ ] **Step 6: Replace the old manuscript description only after gates pass**

The appendix must match actual generator count, constraints, scenarios, and
objective definitions. Retain the synthetic illustration as a separate example
only if explicitly labeled.

- [ ] **Step 7: Verify and commit**

Run: `cd code && python -m pytest tests/test_grid_case.py -v`

```bash
git add code/lexur/cases/grid code/tests/test_grid_case.py data/grid/README.md code/lexur/smartgrid.py paper/sections/B_smartgrid.tex
git commit -m "feat: replace grid illustration with public constrained case"
```

### Task 14: Certificate Usefulness Evaluation

**Files:**
- Create: `study/certificate/protocol.md`
- Create: `study/certificate/materials/`
- Create: `study/certificate/analysis.py`
- Create: `study/certificate/analysis_plan.md`
- Create: `code/tests/test_certificate_study_analysis.py`

**Interfaces:**
- Produces: frozen study protocol, anonymized response schema, and analysis script.

- [ ] **Step 1: Define the decision task and primary outcome**

Use a within- or between-subject comparison of recommendation-only versus
recommendation-plus-certificate. Primary outcome: correct identification of the
most fragile criterion/probe. Secondary outcomes: decision time, calibrated
confidence, explanation accuracy, and perceived usefulness.

- [ ] **Step 2: Conduct an a priori power calculation**

Specify target effect, alpha, power, exclusions, missing-data policy, and one
primary contrast in `analysis_plan.md` before recruitment.

- [ ] **Step 3: Obtain required ethics determination**

Record approval/exemption identifier before collecting human responses. If human
validation is not feasible, remove the decision-aid claim rather than replacing
participants with author judgment.

- [ ] **Step 4: Pilot materials without examining confirmatory outcomes**

Check comprehension, timing, and logging on a small pilot excluded from the final
analysis.

- [ ] **Step 5: Run the frozen analysis**

Report effect sizes, CIs, exclusions, missingness, and all registered outcomes,
including null or adverse results.

- [ ] **Step 6: Commit protocol and analysis separately from private responses**

```bash
git add study/certificate code/tests/test_certificate_study_analysis.py
git commit -m "research: register certificate usefulness evaluation"
```

### Task 15: Full Contribution Synthesis and Audit

**Files:**
- Modify: `code/configs/claims.yaml`
- Modify: `paper/sections/01_intro.tex`
- Modify: `paper/sections/04_direct.tex`
- Modify: `paper/sections/06_extensions.tex`
- Modify: `paper/sections/07_experiments.tex`
- Modify: `paper/sections/08_discussion.tex`
- Modify: `paper/sections/09_conclusion.tex`
- Create: `results/protocol/audit/stage2_audit.md`

**Interfaces:**
- Consumes: Stage 2 exactness, calibration, stakeholder, real-case, and usefulness artifacts.
- Produces: final C1-C10 evidence status and manuscript.

- [ ] **Step 1: Run all unit and property tests in a clean environment**

Run: `cd code && python -m pytest -q`

Expected: all tests pass; solver-dependent skips list their missing solver explicitly.

- [ ] **Step 2: Run pilot versions of every experiment**

Expected: schemas, manifests, gates, and manuscript macros complete without using full-scale outputs.

- [ ] **Step 3: Freeze full configurations and hashes**

No thresholds, exclusions, comparator settings, or primary outcomes change after this point.

- [ ] **Step 4: Execute full runs and independent recomputation audit**

Independently reproduce at least one raw-to-table path for each of C1-C10. Record
whether evidence proves, qualifies, contradicts, or is missing for each claim.

- [ ] **Step 5: Rewrite claims from evidence status**

Only `supported` claims remain unqualified contributions. `Qualified` claims name
their conditions. `Exploratory` claims move to future work. `Unsupported` claims
are removed or explicitly contradicted in limitations.

- [ ] **Step 6: Build and visually inspect the final manuscript**

Run the complete LaTeX build and inspect every table/figure for labels, units,
uncertainty, sample counts, and consistency with generated artifacts.

- [ ] **Step 7: Commit the final audit**

```bash
git add code/configs/claims.yaml paper/sections results/protocol/audit/stage2_audit.md
git commit -m "research: complete full contribution evidence audit"
```

## Milestones and Go/No-Go Decisions

| Milestone | Target | Go condition |
|---|---:|---|
| M1 Infrastructure | End week 1 | Clean environment, tests, provenance, claim registry pass |
| M2 Valid core analysis | End week 3 | Raw schema, blocked inference, probe and normalization studies pass pilot |
| M3 Stage 1 release | End week 6 | C1-C5 audited; paper synchronized; unsupported extension claims narrowed |
| M4 Exact direct methods | End week 9 | LP/MILP certificates match exhaustive small references |
| M5 Extension validity | End week 10 | Stochastic calibration and independent stakeholder metrics pass |
| M6 External validity | End week 13 | Public constrained case reproduces benchmark and multi-regime results |
| M7 Full release | End week 16 | C1-C10 evidence audit and manuscript consistency pass |

## Minimum Submission-Safe Outcome

If Stage 2 is delayed, submit only after M3 with this contribution boundary:

- exact finite candidate-set LexUR;
- transparent certificate and tolerance/stability reporting;
- corrected paired, stratified tail-quality evidence;
- validated redundancy behavior;
- explicit normalization limitations and abstention behavior;
- direct, stochastic, stakeholder, and real-case components labeled exploratory.

This outcome is scientifically stronger than retaining broader claims supported by
proxy or unit-inconsistent experiments.

