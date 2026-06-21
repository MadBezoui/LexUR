# Leximax Universal-Regret (LUR) Core — Reproducibility Package

Reference implementation, experiments, and manuscript for
*Beyond Pareto Fronts: A Leximax Universal-Regret Core for Robust Multicriteria
Decision Support*.

## Layout

```
ALUR/
├── code/                 Python package + runner
│   ├── lur/
│   │   ├── problems.py    Pareto-front + redundant candidate-set generators
│   │   ├── methods.py     LUR + baselines (TOPSIS, CP, knee, RW, ASF, SMAA, MMR)
│   │   ├── metrics.py     held-out mean/tail loss, certificate regret, etc.
│   │   ├── stats.py       Friedman, Nemenyi CD, Wilcoxon-Holm, Cliff's delta
│   │   ├── experiments.py benchmark, redundancy, ablation, sensitivity, figures
│   │   └── smartgrid.py   6-objective stochastic dispatch case study
│   ├── run_all.py        master runner (regenerates every table & figure)
│   └── requirements.txt
├── results/
│   ├── tables/           CSV + JSON outputs (numbers.json consolidates all)
│   └── figures/          PDF figures used in the paper
├── paper/                LaTeX manuscript (article class; elsarticle-ready)
│   ├── main.tex
│   ├── sections/
│   ├── refs.bib
│   └── main.pdf
├── COVER_LETTER.md       EJOR Decision Support cover letter
└── EJOR_Acceptance_Plan.md  strategic plan this work executes
```

## Pre-registered EJOR validation protocol

A frozen, config-driven protocol with automated acceptance gates lives alongside
the original experiments:

```bash
cd code
make protocol                              # pilot scale (configs/ejor_pilot.yaml)
make protocol CFG=configs/ejor_final.yaml  # full pre-registered scale
make reproduce_all                         # protocol + original experiments
# stage-by-stage:
python run_protocol.py --config configs/ejor_pilot.yaml --stage benchmark
#   stages: benchmark redundancy probes gates direct stochastic multistakeholder report
```

Outputs land in `results/protocol/`; the acceptance-gate summary is
`results/protocol/tables/gates_report.csv`. See `PROTOCOL_COMPLIANCE.md` for the
gate-by-gate outcome (11 methods, 10 additive/non-additive families, 8 geometries,
direct LP/MILP computation, stochastic and multi-stakeholder validation).

## Reproduce the original experiments

```bash
cd code
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# run tests
make test

# fast smoke test (reps=5, ~20 s)
make smoke

# full study (reps=30); run stage-by-stage (each stage persists to ../results)
python run_all.py --stage benchmark     # main comparison + stats + CD diagram
python run_all.py --stage redundancy    # redundant-objective benchmark
python run_all.py --stage tables        # per-family, certificate, ablation, probe-reduction
python run_all.py --stage sensitivity   # theta and nadir sensitivity figures
python run_all.py --stage extras        # SMAA agreement + dominated-exclusion check
python run_all.py --stage smartgrid     # case study + certificate figure
# or, all at once:
python run_all.py
```

All randomness is seeded; `results/tables/numbers.json` aggregates every figure
quoted in the paper. Within each replication the held-out test-utility draw is
shared across methods, so all comparisons are paired.

## Build the paper

```bash
cd paper
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

For final EJOR submission, change the first line of `main.tex` to
`\documentclass[review]{elsarticle}` and move the abstract/keywords into the
elsarticle front matter; the body, theorems, tables and figures transfer
unchanged.

## Method summary

| Method | Family | Notes |
|---|---|---|
| TOPSIS, CP, Knee, RW, ASF | classical post-processing | weights/thresholds or front required |
| SMAA | robust MCDA | rank-acceptability over a weight distribution |
| MMR | robust MCDA | Savage minimax regret over a linear weight set |
| **LUR** | proposed | leximax of normalised regret over declared monotone probes + certificate |

Held-out evaluation spans **six** preference families — linear, weighted
Chebyshev, augmented ASF, CES, a non-additive 2-additive **Choquet** integral, and
a **satisficing** threshold utility — reported as mean and tail (CVaR) loss. See
`REVISION_NOTES.md` for the consolidated reviewer remarks addressed in this
version.
