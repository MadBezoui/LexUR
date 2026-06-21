# Figure Remediation Design

## Objective

Repair every substantive, statistical, semantic, accessibility, and rendering defect identified in the 17 figures of `paper/main.pdf`. The rebuilt manuscript must use frozen protocol run `33e81af5a748796ef2103fc0dd280bb7cb3aff6758e86ac49877cc632f036749` as the authoritative source for the broadened benchmark and must prevent figures, captions, and generated manuscript constants from drifting across runs.

## Source Of Truth

The broadened benchmark in Figure 7 consumes only the immutable run directory under `results/protocol/runs/33e81af5a748...`. Its `benchmark_analysis.json` defines 7,200 paired instances, 11 methods, average ranks, and Nemenyi CD 0.1779369. The figure generator, generated LaTeX macros, captions, and manuscript checker must all read the same evidence object.

The controlled mechanistic study in Figures 8-15 remains separate from the broadened protocol. Its corrected data products live under `results/tables/` and are regenerated deterministically from the existing fixed seeds. Captions must identify which study each figure uses.

No figure may read through the mutable `results/protocol/current` symlink during publication generation. Figure 7 reads the immutable `results/protocol/runs/33e81af5a748796ef2103fc0dd280bb7cb3aff6758e86ac49877cc632f036749/` directory directly, and its data contract asserts that every loaded artifact carries that run ID. Generated artifacts include the source run ID, source Git commit, dirty-worktree flag, and configuration/parameter hash in sidecar metadata so provenance can be checked without inspecting the plot visually.

## Figure Architecture

Create one publication-figure module that owns shared styling, validation, CD-diagram layout, confidence intervals, and output metadata. Existing experiment functions continue to produce tabular evidence; plotting functions consume tables rather than embedding scientific calculations in layout code.

Every empirical figure receives a small data contract checked before rendering. Contracts cover required columns, method count, sample count, finite values, expected value ranges, and source run ID where applicable. Plotting uses accessible colors, embedded TrueType fonts, vector geometry where practical, and opaque inset backgrounds.

## Statistical Corrections

### Critical-difference figures

Figure 7 is regenerated from run `33e81af5a748...`, showing exactly 11 methods, CD 0.178, and ranks from the authoritative analysis file. Figure 9 continues to use the 480-instance mechanistic study. Both diagrams use collision-free labels and horizontal non-significance groups. Captions state only groups supported by the computed CD; Figure 9 must say that LexUR groups with CP while MMR and ASF have slightly better average ranks beyond the Nemenyi CD, with negligible paired effect sizes.

### Redundancy and ablation

Figure 11 reports paired-bootstrap 95% confidence intervals, using 2,000 resamples of the replication-level observations, for both grouped and tail loss. It must not label LexUR and ASF as tied without an explicit equivalence or non-inferiority result. Highlight colors must appear in the legend.

Figure 12 displays all five registered ablations, including the null results for `No clustering` and `Mean only`. It reports uncertainty for both loss and certificate regret. The title and caption describe probe-family ablations and do not claim that leximax ordering was ablated.

### Choice distance

Figure 13 replaces raw Euclidean distance with root-mean-square normalized criterion distance:

`sqrt(mean((r_lexur - r_smaa)^2))`.

This metric remains in `[0, 1]` and is comparable across values of `m`. The caption defines the metric and reports exact recommendation agreement separately. The experiment also reports Jaccard overlap between LexUR and SMAA tolerance sets at `tau = 1e-4`, rather than treating near-tied exact indices only as categorically different.

### Nadir sensitivity

Figure 14 uses a paired design. Each replication creates one candidate set and one standardized perturbation direction; every displayed error magnitude scales that same direction. The x value is the realized RMS relative perturbation, so the percentage has a literal interpretation. All levels use identical candidate sets, evaluation utilities, and random streams. The plot reports paired mean quality change with a 2,000-resample paired-bootstrap 95% interval and winner-change rate with a Wilson 95% interval. The manuscript does not call the error bounded unless the generator uses bounded perturbations. The table and figure show the same levels.

### Stochastic recovery

Figure 15 evaluates confidence-aware LexUR using `mu_hat + z_alpha * sd_hat / sqrt(n)` with a declared alpha of 0.95. The experiment reuses each problem across sample sizes, reports 40 problems with five resamples per problem, and adds Wilson 95% intervals over the 200 selections at each sample size. It reports both exact-winner recovery and coverage of the noise-free `tau = 1e-4` tolerance set so near ties are not counted only as failexures. The caption states the Gaussian noise scale and logarithmic x-axis.

## Certificate Corrections

Figures 1 and 17 distinguish the worst probe from secondary lexicographic constraints. A presentation-only binding band `beta = 0.01` defines binding probes as those whose disappointment lies within 0.01 of the maximum; this is explicitly distinguished from the selection tolerance `tau = 1e-4`. Other high entries are called “largest disappointments.” Schematic values are visibly marked illustrative.

Figure 16 renders all probes in the smart-grid certificate, not a top-ten slice. Criterion codes are replaced by semantic labels such as `peak stress`, `non-renewable fraction`, and `max(ramping, peak stress)`. The plot displays the recommendation identifier, probe-family version, tolerance, normalization source, and binding rule. The caption notes that MMR selected the same dispatch in this synthetic case, while the labelled certificate is the additional LexUR output.

Figure 17 either uses the actual Figure 16 probe set and values or is a domain-neutral schematic. It must not combine invented values with smart-grid-specific labels.

## Conceptual Figure Corrections

Figure 2 lists the candidate set, normalization bounds, probe family, clustering rule, and numerical tolerance as declared inputs. Its output is a recommendation only when the verified margin condition holds; otherwise it is a stability or tolerance class.

Figure 4 separates the exact algorithm (`tau = 0`) from tolerance-based reporting. It specifies degenerate-criterion and degenerate-probe handling, preserves probe labels through sorting, and returns either the exact minimizer set or a tolerance class rather than an unspecified unique winner.

Figure 5 is relaid out so every probe-family box is legible. Its wording states that cluster aggregates replace exponential subcoalition aggregates while singleton probes remain for separation.

Figure 6 reports the realized number of nontrivial clusters `c` for every point. Because the current concave data have `c = 0`, the caption explicitly says the plotted adaptive counts reduce to `m + 2`; it does not present those points as evidence of clustering performance. The redundant-objective experiment remains the evidence for clustering behavior.

Figures 3 and 8 retain their scientific content but receive legible scales, non-overlapping labels, and a fully opaque inset. Figure 10 replaces the red-green heatmap with a colorblind-safe sequential palette and removes the undefined “most balanced” claim.

## Rendering And Accessibility

Matplotlib uses `pdf.fonttype = 42` and `ps.fonttype = 42`; no Type 3 fonts may remain in publication figures. Heatmaps are vectorized where feasible or embedded at no less than 300 ppi. Red-green-only encoding is prohibited. Lines, markers, hatching, and text labels must preserve meaning in grayscale.

The final PDF is rendered page-by-page at 200 ppi for overview inspection and figure regions at 300 ppi for detailed inspection. Acceptance requires no clipping, overlap, illegible text, unexplained colors, or caption-to-graphic mismatch.

## Automated Verification

Regression tests must fail before implementation for these conditions:

- Figure 7 evidence does not match run `33e81af5a748...` exactly.
- Figure 9 caption groups methods whose rank gap exceeds CD.
- A manuscript caption or `main.tex` fallback contains a stale hard-coded protocol count or CD.
- Choice distance is dimension-dependent for a repeated coordinate difference.
- Nadir sensitivity does not reuse the same problem at every error level.
- Stochastic confidence penalties omit division by `sqrt(n)`.
- A certificate plot drops probes.
- Registered ablations are omitted from Figure 12.
- Publication PDFs contain Type 3 fonts, raster heatmaps below 300 ppi, or unexpected page/figure counts.

Fast CI runs unit tests, manuscript consistency checks, immutable-run provenance checks, deterministic figure-data contracts, and a LaTeX compilation smoke test. The publication acceptance audit additionally performs deterministic regeneration of every figure, a full LaTeX/bibliography rebuild, `pdfinfo`, `pdffonts`, `pdfimages -list`, text extraction of all 17 captions, 200 ppi overview rendering, 300 ppi detailed figure rendering, and visual inspection of every figure page. The expensive rendering audit is a release gate rather than a per-change CI step.

## Scope Boundaries

This work corrects the figures, the experiment functions directly required to make those figures truthful, and adjacent manuscript claims. It does not rerun or redefine the frozen broadened protocol, introduce new benchmark methods, redesign unrelated tables, or rewrite theoretical results beyond the exact/tolerance distinctions exposed by Figures 2 and 4.

Existing unrelated working-tree changes are preserved. Generated PDFs and tables are updated only through the repaired deterministic pipeline.
