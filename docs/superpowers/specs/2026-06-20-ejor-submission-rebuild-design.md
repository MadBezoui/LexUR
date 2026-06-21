# EJOR Submission Rebuild Design

**Status:** Approved for autonomous execution on 20 June 2026

**Target:** European Journal of Operational Research, Decision Support

**Purpose:** Convert the current ALexUR worktree into the strongest scientifically
defensible EJOR submission that the available evidence supports. Acceptance
cannot be guaranteed; the deliverable is a submission-ready manuscript and
reproducibility package with no known critical evidence, consistency, or build
defect.

## 1. Governing Principle

The rebuild is evidence-first. Raw instance-level records are authoritative.
Statistics, acceptance gates, manuscript macros, tables, figures, and prose are
derived from a single validated run identity. A favorable statement is never
substituted for a failed, missing, stale, or exploratory result.

The existing `2026-06-18-experimental-validation-design.md` remains the
scientific scope specification. This document defines the immediate EJOR release
architecture and resolves the defects found in the current worktree.

## 2. Release Architecture

The release pipeline has five explicit boundaries:

1. **Run identity:** hash the frozen configuration and scientific source files,
   record the Git commit and dirty-state digest, Python and package versions,
   platform, seed, and UTC creation time.
2. **Raw evidence:** write benchmark chunks into a run-specific directory. Each
   row records the run identifier, complete experimental cell, method, utility
   family scope, selected candidate, and losses.
3. **Validated analysis:** reject mixed runs, duplicated method/cell rows,
   incomplete method sets, unknown scopes, non-finite metrics, and unexpected
   factor levels before calculating any statistic.
4. **Claim gates:** calculate every gate from artifacts carrying the same run
   identifier. Missing evidence produces `MISSING`; failed thresholds produce
   `FAIL` or `CHECK`; neither can be promoted to `PASS` by the reporting layer.
5. **Publication output:** generate manuscript constants and evidence tables from
   validated gate output. A consistency command fails on stale hard-coded counts,
   numerical contradictions, unsupported claims, or missing generated inputs.

## 3. Statistical Design

- Candidate set, geometry, dimension, size, replication, utilities, and methods
  remain paired according to the frozen configuration.
- Randomized methods receive deterministic method-specific random streams so
  results do not depend on method ordering.
- The full benchmark contains `3 x 6 x 8 x 50 = 7,200` paired experimental cells
  and 11 methods; reports must not describe it as 2,400 cells.
- Non-inferiority uses the frozen absolute margin of 0.01 on normalized tail
  loss and a cluster bootstrap over complete paired cells. No post-result margin
  selection is allowed.
- Holm-adjusted Wilcoxon comparisons, effect sizes, confidence intervals, and
  stratified estimates are reported together; significance alone is insufficient.
- Nadir sensitivity reuses the same generated problems and held-out utilities at
  every perturbation level. Quality degradation is calculated within instance
  before aggregation.
- Adaptive-probe validation reports predictive loss, certificate error, and
  tolerance-set agreement. Current failed criteria remain visible unless a
  corrected pre-specified experiment produces different evidence.

## 4. Code and Test Boundaries

New or revised behavior is developed test-first. Required integration coverage:

- run identity changes when scientific source changes;
- finalization rejects stale or mixed chunks;
- complete raw frames contain exactly one row per method and paired cell;
- report generation reads the current authoritative analysis artifact;
- claim status preserves failed and missing gates;
- normalization experiments are paired across error levels;
- manuscript constants equal the frozen config and validated raw frame;
- smoke execution regenerates a self-consistent report in an isolated directory.

The complete test command must finish without warnings caused by ALexUR code.
Warnings from degenerate correlation inputs are handled explicitly rather than
ignored globally.

## 5. Manuscript Policy

- Position LexUR as a finite candidate-set, regret-based robust-MCDA recommender,
  not as universally optimal or preference-free.
- Describe the protocol as frozen or pre-specified, not publicly pre-registered,
  unless independent timestamp evidence is available.
- Present non-inferiority against ASF and MMR only when the corrected paired gate
  passes, including its margin and confidence interval.
- Report normalization instability and adaptive-probe limitations prominently.
- Direct LP/MILP, stochastic, multi-stakeholder, and smart-grid claims are labeled
  supported, qualified, or exploratory strictly from the claim registry.
- The smart-grid study is a synthetic dispatch illustration unless it is replaced
  by an externally sourced, physically validated system.
- Manuscript tables and numerical prose must be generated or checked against the
  current run; duplicate hand-maintained summaries are removed.
- The primary manuscript uses EJOR-compatible `elsarticle` review format and is
  kept within the journal limit. Extended proofs and diagnostic tables move to a
  clearly linked supplement if necessary.

## 6. Reproducibility Package

The release provides:

- exact environment constraints and a clean installation command;
- `make test`, `make smoke`, `make protocol`, `make manuscript-check`, and
  `make paper` entry points;
- a run manifest and raw-schema documentation;
- generated gate, claim-status, and manuscript-number artifacts;
- a concise reproduction README distinguishing pilot from full execution;
- no tracked virtual environment, caches, temporary chunks, or LaTeX auxiliaries.

## 7. Acceptance Criteria

The EJOR rebuild is complete only when all of the following are freshly proven:

1. Unit and integration tests pass with no project-generated warnings.
2. Smoke and pilot protocols complete in isolated run directories.
3. The selected full-run raw data pass strict schema and completeness validation.
4. Every report, figure, and manuscript constant traces to that full run.
5. Claim statuses match gate outcomes without forced passes.
6. Manuscript consistency checking finds no stale or contradictory numbers.
7. The EJOR LaTeX manuscript and supplement build without undefined citations,
   references, missing assets, or material overflow.
8. The paper, cover letter, highlights, README, and data/code statement agree on
   contribution, scope, limitations, method count, and experiment count.
9. A final referee-style audit finds no unresolved critical or major issue that
   can be fixed from the available code, data, and author-independent metadata.

Author names, affiliations, funding, conflicts, acknowledgments, and the public
repository/DOI are factual metadata that cannot be inferred. They are collected
in one explicit release checklist rather than fabricated.

## 8. Decision Record

- Preserve existing user changes and work with the current dirty worktree.
- Do not chase favorable outcomes by changing frozen thresholds.
- Prefer narrowing a claim over adding weak evidence.
- Use the complete 7,200-cell data already present only after its source identity
  and schema are validated; otherwise regenerate the affected stages.
- Run smoke and pilot validation before compute-heavy stages.
- Do not promise journal acceptance; optimize for correctness, novelty clarity,
  reproducibility, and reviewer resistance.
