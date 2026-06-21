# Figure Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild all 17 manuscript figures so their evidence, statistical interpretation, labels, accessibility, and PDF rendering satisfy the approved figure-remediation specification.

**Architecture:** Add a focused `lur.figure_evidence` module for immutable evidence loading, corrected metrics, confidence intervals, and provenance. Add a `lur.publication_figures` module for shared accessible styling and rendering, then reduce the existing scripts to deterministic entry points. Update the experiment producers and LaTeX/TikZ sources only where the approved corrections require it.

**Tech Stack:** Python 3, NumPy, pandas, SciPy, Matplotlib, pytest, LaTeX/TikZ, Poppler (`pdfinfo`, `pdffonts`, `pdfimages`, `pdftoppm`).

## Global Constraints

- Frozen protocol run `33e81af5a748796ef2103fc0dd280bb7cb3aff6758e86ac49877cc632f036749` is authoritative for Figure 7.
- Publication generation must not read `results/protocol/current`.
- Existing unrelated working-tree changes must be preserved.
- Matplotlib publication output must use font type 42 and colorblind-safe encodings.
- Exact selection uses `tau = 0`; numerical reporting uses `tau = 1e-4`; the presentation binding band is `beta = 0.01`.
- Fast CI excludes expensive page rendering; the publication acceptance audit includes it.
- Because existing target files were dirty before this work, implementation changes are not committed automatically; only explicitly isolated new files may be committed without user confirmation.

---

### Task 1: Immutable Figure Evidence And Provenance

**Files:**
- Create: `code/lur/figure_evidence.py`
- Create: `code/tests/test_figure_evidence.py`
- Modify: `code/scripts/regen_cd_protocol.py`
- Modify: `paper/main.tex:63-67`

**Interfaces:**
- Produces: `AUTHORITATIVE_RUN_ID`, `load_protocol_evidence(repo_root)`, `figure_provenance(repo_root, run_id, params)`, and `write_sidecar(pdf_path, metadata)`.
- Consumes: immutable `benchmark_analysis.json` and `raw/benchmark.parquet` under the authoritative run directory.

- [ ] **Step 1: Write failing provenance and stale-fallback tests**

```python
def test_protocol_loader_is_pinned_to_authoritative_run(repo_root):
    evidence = load_protocol_evidence(repo_root)
    assert evidence.run_id == AUTHORITATIVE_RUN_ID
    assert evidence.n_instances == 7200
    assert evidence.methods == 11
    assert evidence.nemenyi_cd == pytest.approx(0.1779369200025672)

def test_main_fallback_has_authoritative_cd(repo_root):
    text = (repo_root / "paper/main.tex").read_text()
    assert r"\newcommand{\protocolCD}{0.178}" in text
    assert r"\newcommand{\protocolCD}{0.31}" not in text
```

- [ ] **Step 2: Run tests and verify expected failures**

Run: `cd code && python3 -m pytest tests/test_figure_evidence.py -q`

Expected: FAIL because `lur.figure_evidence` does not exist and the fallback remains `0.31`.

- [ ] **Step 3: Implement immutable evidence loading and metadata**

Use a frozen dataclass holding run ID, method names, ranks, CD, and instance count. Reject mismatched run IDs between analysis and parquet. Hash canonical JSON parameters with SHA-256. Record `git rev-parse HEAD` and `git status --porcelain` without modifying the worktree.

- [ ] **Step 4: Replace Figure 7 generator input and repair fallback constants**

`regen_cd_protocol.py` must call `load_protocol_evidence()` and must not contain the string `results/protocol/current`. Write `paper/cd_protocol.pdf.json` beside the PDF.

- [ ] **Step 5: Run focused and manuscript tests**

Run: `cd code && python3 -m pytest tests/test_figure_evidence.py tests/test_manuscript_check.py -q`

Expected: PASS.

---

### Task 2: Shared Publication Plotting And CD Diagrams

**Files:**
- Create: `code/lur/publication_figures.py`
- Create: `code/tests/test_publication_figures.py`
- Modify: `code/lur/experiments.py:86-102`
- Modify: `code/scripts/regen_cd_protocol.py`

**Interfaces:**
- Produces: `publication_style()`, `significance_groups(ranks, cd)`, `render_cd_diagram(...)`, `paired_bootstrap_ci(...)`, and `wilson_interval(...)`.
- Consumes: evidence objects and output paths from Task 1.

- [ ] **Step 1: Write failing tests for CD groups, collision-safe rows, intervals, and fonts**

```python
def test_mechanistic_cd_only_groups_lur_with_cp():
    ranks = {"MMR": 2.8521, "ASF": 2.9385, "CP": 3.4208, "LUR": 3.4406}
    groups = significance_groups(ranks, 0.479243)
    lur_groups = [set(g) for g in groups if "LUR" in g]
    assert {"CP", "LUR"} in lur_groups
    assert not any({"MMR", "LUR"} <= g for g in lur_groups)
    assert not any({"ASF", "LUR"} <= g for g in lur_groups)

def test_publication_style_uses_truetype_fonts():
    with publication_style():
        assert matplotlib.rcParams["pdf.fonttype"] == 42
```

- [ ] **Step 2: Run tests and verify expected failures**

Run: `cd code && python3 -m pytest tests/test_publication_figures.py -q`

Expected: FAIL because shared publication helpers do not exist.

- [ ] **Step 3: Implement shared style and robust CD layout**

Use alternating left/right label columns with connector lines, not text placed directly under rank ticks. Draw maximal contiguous non-significance bars computed from pairwise rank gaps `<= CD`. Use Okabe-Ito colors and retain marker/line distinctions in grayscale.

- [ ] **Step 4: Route both CD figures through the shared renderer**

Figure 7 receives the authoritative 11-method evidence. Figure 9 receives `results/tables/stats_summary.json`. Generate sidecars for both.

- [ ] **Step 5: Verify focused tests and extracted PDF labels**

Run: `cd code && python3 -m pytest tests/test_publication_figures.py -q && pdftotext -layout ../paper/cd_protocol.pdf -`

Expected: PASS; extracted Figure 7 labels contain 11 unique method names and `CD=0.178`.

---

### Task 3: Correct Mechanistic Metrics And Paired Experiments

**Files:**
- Modify: `code/lur/experiments.py:113-150,205-230,281-371`
- Modify: `code/lur/extras_validation.py:11-40`
- Create: `code/tests/test_figure_experiments.py`

**Interfaces:**
- Produces tables containing replication-level observations, 95% intervals, normalized choice distance, paired nadir diagnostics, exact recovery, and tolerance-set coverage.
- Consumes: `paired_bootstrap_ci`, `wilson_interval`, and existing deterministic problem generators.

- [ ] **Step 1: Write failing tests for corrected metrics**

```python
def test_rms_choice_distance_is_dimension_invariant():
    a3, b3 = np.zeros(3), np.full(3, 0.5)
    a12, b12 = np.zeros(12), np.full(12, 0.5)
    assert rms_choice_distance(a3, b3) == pytest.approx(0.5)
    assert rms_choice_distance(a12, b12) == pytest.approx(0.5)

def test_confidence_adjustment_uses_standard_error():
    mu = np.zeros((1, 2)); sd = np.ones((1, 2))
    adjusted = confidence_adjusted_objectives(mu, sd, n_obs=100, z=1.6449)
    assert adjusted[0, 0] == pytest.approx(0.16449)

def test_nadir_levels_reuse_problem_ids(tmp_path):
    df = sensitivity_nadir(reps=3, error_levels=(0, .1, .2), outdir=tmp_path)
    assert df.groupby("problem_id")["error_level"].nunique().eq(3).all()
```

- [ ] **Step 2: Run tests and verify expected failures**

Run: `cd code && python3 -m pytest tests/test_figure_experiments.py -q`

Expected: FAIL on raw Euclidean distance, missing standard-error adjustment, and unpaired nadir data.

- [ ] **Step 3: Implement replication-level redundancy and ablation outputs**

Persist long-form observations before aggregation. Compute 2,000-resample paired-bootstrap intervals for grouped/tail loss and loss/certificate regret. Keep all five ablations in registered order.

- [ ] **Step 4: Implement normalized distance and tolerance overlap**

Replace `np.linalg.norm(delta)` with `sqrt(mean(delta**2))`. Add exact agreement and `tau=1e-4` tolerance-set Jaccard columns.

- [ ] **Step 5: Implement paired nadir sensitivity**

For each problem, draw one perturbation vector, center and scale it to unit RMS, and reuse it across all error levels. Reuse candidate sets and held-out utility caches. Return long-form problem-level loss change and flip indicators plus aggregated intervals.

- [ ] **Step 6: Implement confidence-aware stochastic recovery**

Use `mu_hat + 1.6449 * sd_hat / sqrt(n_obs)`. Reuse each of 40 problem instances across sample sizes and perform five resamples. Report exact recovery and membership in the noise-free `tau=1e-4` tolerance set with Wilson intervals.

- [ ] **Step 7: Run focused tests**

Run: `cd code && python3 -m pytest tests/test_figure_experiments.py tests/test_methods.py -q`

Expected: PASS.

---

### Task 4: Rebuild Empirical Figures 6-15

**Files:**
- Modify: `code/scripts/make_paper_figures.py`
- Modify: `code/run_all.py`
- Modify: `paper/sections/05_probes.tex:121-155`
- Modify: `paper/sections/07_experiments.tex:106-397`
- Modify generated tables and PDFs under `results/tables/`, `results/figures/`, and `paper/`

**Interfaces:**
- Consumes corrected tables from Task 3 and plotting utilities from Task 2.
- Produces Figures 6-15 and provenance sidecars.

- [ ] **Step 1: Write failing static figure-contract tests**

Add assertions that Figure 6 exposes `c`, Figure 12 includes five ablations, Figure 13 distances lie in `[0,1]`, Figure 14 has identical problem IDs at every level, Figure 15 includes lower/upper interval columns, and captions contain the corrected statistical claims.

- [ ] **Step 2: Run contract tests and verify failures**

Run: `cd code && python3 -m pytest tests/test_publication_figures.py::TestFigureContracts -q`

Expected: FAIL against current tables/captions.

- [ ] **Step 3: Repair layouts and captions**

Use an opaque inset and external labels in Figure 8; a blue sequential heatmap in Figure 10; defined intervals and legends in Figure 11; all ablations in Figure 12; RMS distance and overlap annotations in Figure 13; paired changes and intervals in Figure 14; and dual recovery/coverage curves with intervals in Figure 15. Figure 6 explicitly labels `c=0` and `K=m+2`.

- [ ] **Step 4: Regenerate corrected tables and figures deterministically**

Run: `cd code && python3 run_all.py`

Expected: exit 0 and stable regenerated outputs.

- [ ] **Step 5: Run contract tests**

Run: `cd code && python3 -m pytest tests/test_publication_figures.py::TestFigureContracts -q`

Expected: PASS.

---

### Task 5: Repair Conceptual Figures And Algorithm Semantics

**Files:**
- Modify: `paper/tikz/fig_pareto_cert.tex`
- Modify: `paper/tikz/fig_pipeline.tex`
- Modify: `paper/tikz/fig_leximax.tex`
- Modify: `paper/tikz/fig_probes.tex`
- Modify: `paper/tikz/fig_cert_concept.tex`
- Modify: `paper/sections/04_direct.tex:12-43`
- Modify: `paper/sections/01_intro.tex`

**Interfaces:**
- Produces corrected Figures 1-5 and 17.
- Consumes exact/tolerance terminology from the approved specification.

- [ ] **Step 1: Write failing manuscript semantic checks**

Assert that the pipeline contains `stability class`, the exact algorithm states `tau=0`, the reporting step returns a `tau-class`, the probe caption does not say cluster probes replace member singletons, and schematic certificate figures contain `illustrative` plus `beta=0.01`.

- [ ] **Step 2: Run checks and verify expected failures**

Run: `cd code && python3 -m pytest tests/test_manuscript_check.py -q`

Expected: FAIL on current wording.

- [ ] **Step 3: Apply scoped TikZ and algorithm edits**

Relayout Figure 5 with fixed-width stacked nodes and adequate vertical spacing. Preserve named probe labels through Figure 4 sorting. Separate exact minimizer computation from tolerance reporting. Use “largest disappointments” unless the `beta=0.01` rule is met.

- [ ] **Step 4: Compile TikZ figures through the manuscript**

Run: `make -C code paper`

Expected: LaTeX exits 0 with no overfull figure boxes.

- [ ] **Step 5: Run semantic checks**

Run: `cd code && python3 -m pytest tests/test_manuscript_check.py -q`

Expected: PASS.

---

### Task 6: Complete And Semantic Smart-Grid Certificate

**Files:**
- Modify: `code/lur/smartgrid.py:142-168`
- Modify: `code/tests/test_smartgrid.py`
- Modify: `paper/sections/07_experiments.tex:399-417`
- Modify: `paper/tikz/fig_cert_concept.tex`

**Interfaces:**
- Produces: complete semantic certificate table and Figure 16.
- Consumes: objective names, all certificate rows, `tau=1e-4`, and `beta=0.01`.

- [ ] **Step 1: Write failing complete-certificate tests**

```python
def test_certificate_plot_keeps_every_probe(tmp_path):
    summary = run_case(outdir=tmp_path)
    plotted = json.loads((tmp_path / "figures/certificate.pdf.json").read_text())
    assert plotted["probe_count"] == len(summary["certificate"])
    assert plotted["omitted_probe_count"] == 0
    assert all("f" not in label for label in plotted["display_labels"])
```

- [ ] **Step 2: Run test and verify failure**

Run: `cd code && python3 -m pytest tests/test_smartgrid.py -q`

Expected: FAIL because the current plot slices `cert[:10]` and uses criterion codes.

- [ ] **Step 3: Render all probes with semantic labels and audit metadata**

Map codes to objective names recursively in singleton, mean, and max probe labels. Highlight only values within `beta=0.01` of the maximum. Include candidate index 104, bounds source, `tau`, `beta`, and probe count in the sidecar. State in the caption that MMR selected the same dispatch.

- [ ] **Step 4: Make Figure 17 domain-neutral**

Use generic cost, emissions, reliability, and coalition labels with visibly illustrative values; do not claim they follow the smart-grid case.

- [ ] **Step 5: Run smart-grid and manuscript tests**

Run: `cd code && python3 -m pytest tests/test_smartgrid.py tests/test_manuscript_check.py -q`

Expected: PASS.

---

### Task 7: Fast CI And Publication Preflight

**Files:**
- Create: `code/scripts/preflight_figures.py`
- Create: `code/tests/test_figure_preflight.py`
- Modify: `code/Makefile`
- Modify: `code/lur/manuscript.py`

**Interfaces:**
- Produces: `make figure-check` for fast CI and `make publication-audit` for the release gate.
- Consumes: final `paper/main.pdf`, sidecars, Poppler tools, and extracted captions.

- [ ] **Step 1: Write failing preflight tests**

Test 17 captions, 17 figure numbers, authoritative Figure 7 provenance, absence of Type 3 fonts, no raster image below 300 ppi, and no stale `0.31` fallback.

- [ ] **Step 2: Run tests and verify expected failures**

Run: `cd code && python3 -m pytest tests/test_figure_preflight.py -q`

Expected: FAIL on current Type 3 fonts, 190 ppi heatmap, and stale fallback.

- [ ] **Step 3: Implement fast and release-gate commands**

`figure-check` runs unit/data/manuscript checks and a one-pass LaTeX smoke compile. `publication-audit` regenerates all figures, performs the full four-pass manuscript build, runs Poppler preflight, and renders overview/detail PNGs into `tmp/pdfs/publication-audit/`.

- [ ] **Step 4: Run the complete Python suite**

Run: `cd code && python3 -m pytest -q`

Expected: all tests pass.

---

### Task 8: Rebuild And Visual Acceptance Audit

**Files:**
- Regenerate: `paper/main.pdf`, all `paper/fig_*.pdf`, `paper/cd_*.pdf`, `paper/certificate.pdf`, and corresponding result artifacts.
- Generate temporary audit renders under `tmp/pdfs/publication-audit/`.

**Interfaces:**
- Consumes all preceding tasks.
- Produces final publication PDF and verification report.

- [ ] **Step 1: Run the publication audit**

Run: `make -C code publication-audit`

Expected: exit 0; 17 captions; no Type 3 fonts; no sub-300-ppi raster; authoritative provenance passes.

- [ ] **Step 2: Inspect every figure page at overview resolution**

Inspect PDF pages 2, 6, 8, 10, 11, 13, and 16-24 from `tmp/pdfs/publication-audit/pages-200/`.

- [ ] **Step 3: Inspect every figure crop at 300 ppi**

Confirm no overlap, clipping, illegible labels, unexplained encodings, or caption mismatch. If a defect remains, add a failing regression or contract check before fixing it.

- [ ] **Step 4: Run final clean verification**

Run: `cd code && python3 -m pytest -q && make manuscript-check && cd .. && pdfinfo paper/main.pdf && pdffonts paper/main.pdf && pdfimages -list paper/main.pdf`

Expected: tests and manuscript check pass; PDF contains 17 figures, no Type 3 fonts, and no raster below 300 ppi.

- [ ] **Step 5: Review the final diff without reverting unrelated work**

Run: `git status --short && git diff --check && git diff --stat`

Expected: only intended figure/manuscript/test/generated artifacts are newly changed by this implementation; pre-existing unrelated modifications remain intact.
