# EJOR Submission Rebuild Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an evidence-consistent, reproducible, submission-ready EJOR Decision Support manuscript and ALexUR validation package.

**Architecture:** A run identity binds configuration, scientific source, environment, and output directory. Strict raw-record validation feeds one authoritative analysis artifact, which feeds claim gates and generated manuscript constants; no reporting layer can override evidence. Experiment fixes are developed with regression tests, then smoke, pilot, and validated full artifacts are executed in that order.

**Tech Stack:** Python 3.11, NumPy 1.26, SciPy 1.13, pandas 2.2, PyYAML 6, PuLP 2.9/CBC, Matplotlib 3.9, PyArrow, pytest, pytest-cov, LaTeX/elsarticle.

## Global Constraints

- Preserve all existing user changes; stage and commit only files intentionally changed by this plan.
- Use ASCII in code and generated machine-readable artifacts.
- Preserve seeded, paired comparisons across methods and experimental cells.
- Freeze non-inferiority at an absolute margin of 0.01 normalized tail loss.
- Never silently combine raw chunks from different run identities.
- Never promote missing, failed, or acknowledged-limit evidence to `PASS`.
- Treat raw instance-level records as authoritative and aggregate outputs as derived.
- Describe the existing smart-grid case as a synthetic illustration.
- Do not fabricate authors, affiliations, funding, conflicts, repository URLs, DOIs, expert validation, or preregistration.
- Run smoke and pilot validation before compute-heavy full execution.

---

### Task 1: Scientific Run Identity

**Files:**
- Modify: `code/lexur/provenance.py`
- Modify: `code/tests/test_provenance.py`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Consumes: config path and repository root.
- Produces: `build_manifest(config_path, seed, source_root=None) -> dict` containing `run_id`, `source_sha256`, `dirty_sha256`, `created_utc`, and existing environment fields.

- [ ] **Step 1: Write failing identity tests**

```python
def test_source_fingerprint_changes_when_scientific_code_changes(tmp_path):
    root = tmp_path / "repo"
    (root / "code" / "lexur").mkdir(parents=True)
    source = root / "code" / "lexur" / "methods.py"
    source.write_text("VALUE = 1\n", encoding="utf-8")
    first = source_fingerprint(root)
    source.write_text("VALUE = 2\n", encoding="utf-8")
    assert source_fingerprint(root) != first


def test_manifest_run_id_binds_config_and_source(tmp_path):
    root = tmp_path / "repo"
    (root / "code" / "lexur").mkdir(parents=True)
    (root / "code" / "lexur" / "methods.py").write_text("VALUE = 1\n")
    cfg = root / "code" / "config.yaml"
    cfg.write_text("seed: 17\n")
    manifest = build_manifest(str(cfg), 17, source_root=root)
    assert len(manifest["run_id"]) == 64
    assert manifest["source_sha256"]
    assert manifest["created_utc"].endswith("Z")
```

- [ ] **Step 2: Verify RED**

Run: `cd code && .venv/bin/python -m pytest tests/test_provenance.py -v`

Expected: fail because `source_fingerprint` and the extended manifest contract do not exist.

- [ ] **Step 3: Implement deterministic source and dirty fingerprints**

```python
SCIENTIFIC_PATTERNS = (
    "code/lexur/*.py", "code/run_protocol.py", "code/run_all.py",
    "code/configs/*.yaml", "code/pyproject.toml",
)


def source_fingerprint(root: str | Path) -> str:
    root = Path(root).resolve()
    digest = hashlib.sha256()
    paths = sorted({p for pattern in SCIENTIFIC_PATTERNS for p in root.glob(pattern)})
    for path in paths:
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
```

Use `git diff --binary -- code ':!code/tests'` for `dirty_sha256`. Define
`run_id = sha256(config_sha256 + source_sha256 + dirty_sha256 + seed)` and record
UTC time with `datetime.now(timezone.utc)`.

- [ ] **Step 4: Verify GREEN**

Run: `cd code && .venv/bin/python -m pytest tests/test_provenance.py -v`

Expected: all provenance tests pass.

- [ ] **Step 5: Route protocol output by run identity**

Add `--output-root`; default to `../results/protocol`. Write run-specific raw and
temporary data under `<output-root>/runs/<run-id>/`, and publish validated derived
artifacts to `<output-root>/current/` only after finalization succeeds.

- [ ] **Step 6: Commit**

```bash
git add code/lexur/provenance.py code/tests/test_provenance.py code/run_protocol.py
git commit -m "feat: bind protocol artifacts to scientific run identity"
```

### Task 2: Strict Raw Record and Chunk Validation

**Files:**
- Modify: `code/lexur/records.py`
- Modify: `code/tests/test_records.py`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Consumes: tidy benchmark frame, config, expected run ID.
- Produces: `validate_benchmark_frame(frame, cfg, run_id) -> None` and `load_validated_chunks(paths, cfg, run_id) -> DataFrame`.

- [ ] **Step 1: Add failing validation tests**

```python
def test_validation_rejects_missing_method_in_one_cell(complete_frame, cfg):
    broken = complete_frame.drop(complete_frame.index[-1])
    with pytest.raises(ValueError, match="method set"):
        validate_benchmark_frame(broken, cfg, "run-a")


def test_validation_rejects_mixed_run_ids(complete_frame, cfg):
    broken = complete_frame.copy()
    broken.loc[broken.index[-1], "run_id"] = "run-b"
    with pytest.raises(ValueError, match="run_id"):
        validate_benchmark_frame(broken, cfg, "run-a")


def test_validation_rejects_unknown_utility_scope(complete_frame, cfg):
    broken = complete_frame.copy()
    broken.loc[broken.index[0], "utility_scope"] = "unknown"
    with pytest.raises(ValueError, match="utility_scope"):
        validate_benchmark_frame(broken, cfg, "run-a")
```

- [ ] **Step 2: Verify RED**

Run: `cd code && .venv/bin/python -m pytest tests/test_records.py -v`

Expected: validation accepts at least one invalid frame.

- [ ] **Step 3: Implement complete schema validation**

Validate exact factor levels, one row for every
`(N,m,geometry,replication,method)`, no duplicates, exact method set per cell,
single expected run/config identity, allowed scopes, finite loss values in
`[0,1]`, selected indices in `[0,N)`, and the expected total row count.

- [ ] **Step 4: Validate chunk metadata before concatenation**

`load_validated_chunks` must reject empty lists, schema differences, mixed IDs,
overlapping cells, and partial final collections. It returns rows in stable factor
order so results do not depend on filesystem ordering.

- [ ] **Step 5: Verify GREEN and regression suite**

Run: `cd code && .venv/bin/python -m pytest tests/test_records.py tests/test_provenance.py -v`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add code/lexur/records.py code/tests/test_records.py code/run_protocol.py
git commit -m "fix: reject incomplete or mixed benchmark evidence"
```

### Task 3: Authoritative Benchmark Analysis and Reporting

**Files:**
- Create: `code/lexur/reporting.py`
- Create: `code/tests/test_reporting.py`
- Modify: `code/run_protocol.py`
- Modify: `code/lexur/analysis.py`

**Interfaces:**
- Consumes: validated raw benchmark frame and frozen config.
- Produces: `analyze_benchmark(frame, cfg) -> dict`, `build_gate_report(artifacts, cfg, run_id) -> list[dict]`.

- [ ] **Step 1: Write a failing stale-statistics regression test**

```python
def test_gate_report_uses_current_noninferiority_artifact(tmp_path):
    current = {"run_id": "new", "noninferiority": {
        "ASF": {"noninferior": True, "mean_diff": 0.001, "ci": [-0.001, 0.003]},
        "MMR": {"noninferior": True, "mean_diff": 0.002, "ci": [0.0, 0.004]},
    }}
    stale = {"run_id": "old", "noninferiority": {
        "ASF": {"noninferior": False}, "MMR": {"noninferior": False},
    }}
    rows = build_gate_report({"benchmark_analysis": current,
                              "benchmark_stats": stale}, cfg={}, run_id="new")
    assert gate(rows, "tail_noninferiority_asf")["result"] == "PASS"
```

- [ ] **Step 2: Verify RED**

Run: `cd code && .venv/bin/python -m pytest tests/test_reporting.py -v`

Expected: fail because there is no authoritative reporting API.

- [ ] **Step 3: Implement one benchmark analysis artifact**

`analyze_benchmark` returns run ID, design counts, global summaries, average
ranks, Friedman result, Nemenyi CD, Holm-Wilcoxon results, effect sizes,
cluster-bootstrap non-inferiority, and stratified effects. Write it once as
`benchmark_analysis.json`; remove the report dependency on `benchmark_stats.json`
and separate `gates_noninferiority.json`.

- [ ] **Step 4: Implement evidence-preserving gate states**

Gate states are `PASS`, `CHECK`, `FAIL`, and `MISSING`. Each row carries
`run_id`, `gate`, `result`, `threshold`, `estimate`, and `detail`. Artifact run-ID
mismatch raises `ValueError`; absent evidence yields `MISSING`.

- [ ] **Step 5: Verify GREEN**

Run: `cd code && .venv/bin/python -m pytest tests/test_reporting.py tests/test_stats.py -v`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add code/lexur/reporting.py code/tests/test_reporting.py code/lexur/analysis.py code/run_protocol.py
git commit -m "fix: derive protocol reports from authoritative analysis"
```

### Task 4: Honest Claim Registry and Manuscript Checker

**Files:**
- Modify: `code/lexur/claim_gate.py`
- Modify: `code/tests/test_claim_gate.py`
- Rewrite: `code/scripts/check_manuscript_numbers.py`
- Create: `code/tests/test_manuscript_check.py`
- Modify: `code/Makefile`

**Interfaces:**
- Consumes: config, validated analysis, gate report, claims YAML, manuscript tree.
- Produces: generated LaTeX macros/tables, `claim_status.json`, nonzero exit on contradiction.

- [ ] **Step 1: Write failing claim-state tests**

```python
def test_limitation_acknowledged_is_qualified_not_supported():
    claim = {"gates": ["adaptive"]}
    gates = {"adaptive": {"pass": False, "result": "CHECK"}}
    assert summarize_claim(claim, gates) == "qualified"


def test_missing_required_gate_is_exploratory():
    assert summarize_claim({"gates": ["missing"]}, {}) == "exploratory"
```

- [ ] **Step 2: Write failing manuscript contradiction test**

```python
def test_checker_rejects_stale_instance_count(tmp_path):
    tex = tmp_path / "main.tex"
    tex.write_text("The protocol contains 2,400 instances.")
    result = check_manuscript(tex, evidence_for(instances=7200))
    assert any("2,400" in error for error in result.errors)
```

- [ ] **Step 3: Verify RED**

Run: `cd code && .venv/bin/python -m pytest tests/test_claim_gate.py tests/test_manuscript_check.py -v`

Expected: forced-pass or missing checker behavior fails.

- [ ] **Step 4: Implement checker and generated publication inputs**

Generate `paper/generated/protocol_numbers.tex`, `protocol_gates.tex`, and
`protocol_results.tex` from matching-run evidence. Scan all manuscript sections,
README, compliance report, and cover letter for stale registered numerical
phrases. Do not hard-code CD, ranks, confidence bounds, method counts, geometry
counts, or instance counts in the checker.

- [ ] **Step 5: Add Make target**

```make
manuscript-check:
	$(PY) scripts/check_manuscript_numbers.py \
		--paper ../paper --results ../results/protocol/current
```

- [ ] **Step 6: Verify GREEN**

Run: `cd code && .venv/bin/python -m pytest tests/test_claim_gate.py tests/test_manuscript_check.py -v`

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add code/lexur/claim_gate.py code/tests/test_claim_gate.py code/scripts/check_manuscript_numbers.py code/tests/test_manuscript_check.py code/Makefile
git commit -m "fix: prevent unsupported manuscript claims"
```

### Task 5: Paired Sensitivity and Order-Independent Randomness

**Files:**
- Modify: `code/lexur/gates.py`
- Create: `code/tests/test_gates.py`
- Modify: `code/run_protocol.py`

**Interfaces:**
- Consumes: frozen experiment config and master seed.
- Produces: paired nadir diagnostics and deterministic method-specific streams.

- [ ] **Step 1: Write a failing pairing test**

```python
def test_nadir_gate_reuses_problem_identity_across_error_levels(monkeypatch):
    seen = []
    original = problems.make_candidate_set
    def record(*args, **kwargs):
        value = original(*args, **kwargs)
        seen.append(value.copy())
        return value
    monkeypatch.setattr(problems, "make_candidate_set", record)
    gate_nadir_error([0.0, 0.1, 0.2], reps=4, n=20, m=3, n_test=10)
    assert len(seen) == 4
```

- [ ] **Step 2: Write a failing method-order test**

Run the same benchmark cell with the method list forward and reversed; after
sorting by method, `selected_index`, `mean_loss`, and `tail_loss` must match.

- [ ] **Step 3: Verify RED**

Run: `cd code && .venv/bin/python -m pytest tests/test_gates.py -v`

Expected: current nadir gate generates `reps * errors` candidate sets or method
order changes randomized outcomes.

- [ ] **Step 4: Implement paired nadir design**

Loop over replication first. Generate one candidate set, one held-out cache, and
one standard-normal perturbation vector per instance; evaluate every registered
error on that instance. Store instance-level baseline loss, perturbed loss,
paired degradation, flip, and certificate gap before aggregation.

- [ ] **Step 5: Implement method-specific RNG**

Derive each selection stream from `SeedSequence([cell_seed, stable_method_id])`.
Never use Python's randomized `hash()`. Keep common held-out utility draws paired.

- [ ] **Step 6: Verify GREEN**

Run: `cd code && .venv/bin/python -m pytest tests/test_gates.py tests/test_methods.py -v`

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add code/lexur/gates.py code/tests/test_gates.py code/run_protocol.py
git commit -m "fix: pair sensitivity experiments and random streams"
```

### Task 6: Clean Test and Packaging Baseline

**Files:**
- Modify: `code/lexur/methods.py`
- Modify: `code/tests/test_methods.py`
- Modify: `code/pyproject.toml`
- Modify: `code/requirements.txt`
- Modify: `code/requirements-dev.txt`
- Modify: `.gitignore`
- Modify: `README.md`

**Interfaces:**
- Consumes: Python 3.11 environment.
- Produces: warning-free tests, consistent dependency constraints, clean workspace rules.

- [ ] **Step 1: Make correlation warning tests strict**

Wrap constant-column and single-candidate calls in
`warnings.simplefilter("error", RuntimeWarning)` and verify current code fails.

- [ ] **Step 2: Handle degenerate correlations without NumPy warnings**

Standardize only nonconstant columns, define constant columns as uncorrelated
except with themselves, and return singleton clusters for a one-row matrix.

- [ ] **Step 3: Align dependency files**

Keep the `pyproject.toml` version ranges authoritative; make
`requirements.txt` install `-e .`; pin pytest/pytest-cov/pyarrow compatible
ranges in `requirements-dev.txt`.

- [ ] **Step 4: Ignore generated local state**

Add `.venv/`, `*.egg-info/`, `.coverage*`, `.pytest_cache/`,
`paper/generated/`, protocol run/temp directories, and platform metadata to
`.gitignore`. Do not delete user data.

- [ ] **Step 5: Verify**

Run: `cd code && .venv/bin/python -m pytest -W error::RuntimeWarning -q`

Expected: all tests pass without RuntimeWarning.

- [ ] **Step 6: Commit**

```bash
git add .gitignore README.md code/lexur/methods.py code/tests/test_methods.py code/pyproject.toml code/requirements.txt code/requirements-dev.txt
git commit -m "chore: establish clean reproducibility baseline"
```

### Task 7: Smoke, Pilot, and Full Evidence Execution

**Files:**
- Modify as generated: `results/protocol/current/**`
- Modify as generated: `paper/generated/**`
- Modify: `PROTOCOL_COMPLIANCE.md`

**Interfaces:**
- Consumes: validated pipeline and frozen configs.
- Produces: complete run artifacts and an evidence-consistent compliance report.

- [ ] **Step 1: Run full unit and integration suite**

Run: `cd code && .venv/bin/python -m pytest -W error::RuntimeWarning -q`

Expected: zero failexures and zero RuntimeWarning.

- [ ] **Step 2: Execute isolated smoke protocol**

Run: `cd code && .venv/bin/python run_protocol.py --config configs/_smoke.yaml --stage all --output-root ../results/protocol-smoke`

Expected: every required smoke artifact has one run ID and report generation exits 0.

- [ ] **Step 3: Execute pilot protocol**

Run: `cd code && .venv/bin/python run_protocol.py --config configs/ejor_pilot.yaml --stage all --output-root ../results/protocol-pilot`

Expected: strict finalization passes; failed scientific gates remain visible.

- [ ] **Step 4: Validate existing full raw evidence**

Run the strict validator against `results/protocol/raw/benchmark.parquet`. If its
source identity cannot be proven or its scopes remain `unknown`, regenerate the
full benchmark chunks. Never patch unknown scopes after the fact.

- [ ] **Step 5: Execute or finalize the full frozen protocol**

Use `configs/ejor_final.yaml`, method-specific RNGs, and full utility counts.
Chunk only by registered candidate size/dimension/geometry; validate all 7,200
cells before publishing `current/`.

- [ ] **Step 6: Generate compliance report from current gates**

The report states the exact run ID, cell/method counts, all PASS/CHECK/FAIL/MISSING
gates, and claim statuses. It contains no manually substituted result.

- [ ] **Step 7: Commit reproducible derived artifacts only**

Do not commit raw temporary chunks. Commit compact final CSV/JSON/PDF results and
the manifest according to the repository's documented artifact policy.

### Task 8: EJOR Manuscript and Submission Package

**Files:**
- Modify: `paper/main.tex`
- Modify: `paper/sections/*.tex`
- Modify: `paper/refs.bib`
- Create: `paper/supplement.tex`
- Modify: `COVER_LETTER.md`
- Create: `HIGHLIGHTS.md`
- Create: `SUBMISSION_CHECKLIST.md`
- Modify: `README.md`
- Modify: `PROTOCOL_COMPLIANCE.md`

**Interfaces:**
- Consumes: current generated evidence and claim statuses.
- Produces: EJOR review manuscript, supplement, cover letter, highlights, and factual metadata checklist.

- [ ] **Step 1: Replace hard-coded protocol results with generated inputs**

Import `generated/protocol_numbers.tex`, `protocol_gates.tex`, and
`protocol_results.tex`. Remove duplicate manually maintained protocol numbers.

- [ ] **Step 2: Correct scientific positioning**

State the finite candidate-set contribution, auditable regret certificate,
competitive tail behavior, and explicit limits. Replace unsupported universal,
preregistered, direct-MILP, real-case, and adaptive-approximation claims with the
status proven by the registry.

- [ ] **Step 3: Convert to EJOR-compatible elsarticle structure**

Use `\documentclass[review,12pt]{elsarticle}`, journal front matter, author
placeholders centralized in one metadata block, highlights, keywords, data/code
availability, declaration of interests, and supplement references. Keep missing
factual author metadata visibly listed in `SUBMISSION_CHECKLIST.md`.

- [ ] **Step 4: Move overflow material to supplement**

Keep the primary paper within 30 pages including references. Move extended
proofs, full stratified tables, and diagnostics without breaking theorem or table
references.

- [ ] **Step 5: Run manuscript consistency and builds**

Run:

```bash
cd code && .venv/bin/python scripts/check_manuscript_numbers.py --paper ../paper --results ../results/protocol/current
cd ../paper && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
```

Expected: checks and builds exit 0, no undefined citations/references, missing
assets, or overfull boxes wider than 5 pt.

- [ ] **Step 6: Commit**

Stage only manuscript, generated compact evidence, submission documents, and
documentation intentionally changed by this task.

### Task 9: Independent-Style Completion Audit

**Files:**
- Create: `EJOR_RELEASE_AUDIT.md`

**Interfaces:**
- Consumes: complete current worktree, design, plan, evidence, rendered PDFs.
- Produces: requirement-by-requirement proof and remaining author-only metadata.

- [ ] **Step 1: Verify every design acceptance criterion**

For each criterion in the design, record the exact command/artifact, current
result, and whether it proves, contradicts, or fails to prove completion.

- [ ] **Step 2: Perform referee-style review**

Review title, abstract, novelty, robust-MCDA positioning, theory, experimental
design, statistics, construct validity, results, limitations, references,
figures, reproducibility, and EJOR fit. Fix every critical or major issue that
does not require unavailable author facts or external human-subject evidence.

- [ ] **Step 3: Inspect rendered PDFs visually**

Render all pages to images and inspect for clipping, overflow, illegible labels,
broken tables, inconsistent fonts, and missing assets.

- [ ] **Step 4: Run final verification from a clean process**

Run all tests, smoke protocol, manuscript checker, primary build, supplement
build, `git diff --check`, and artifact provenance validation again. Record exact
outputs in `EJOR_RELEASE_AUDIT.md`.

- [ ] **Step 5: Commit final audit**

```bash
git add EJOR_RELEASE_AUDIT.md
git commit -m "docs: record EJOR release verification"
```
