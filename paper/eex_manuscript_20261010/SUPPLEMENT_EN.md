# Online Resource 1

## Source provenance, diagnostics and reporting boundaries

This appendix accompanies *Bid and award dispersion in European carbon auctions*. It reports completed analyses from the fixed research record. Preparation of the manuscript introduced no new regression, resampling draw, sample restriction or market dataset. Tables are transcribed programmatically from frozen JSON outputs, and the accompanying numeric ledger records their source fields.

### S.1. Fixed inputs and completed analyses

The repository is `124-creator/-123`. The input commit is `5745eb3ddca79602346053446583d794b0e09800`; the principal results commit is `e25c1e02e1a58e0aec1084f7419066855e9565ec`; the robustness extension is fixed at `d4b26f1bbd8c1d7c036259e48e119c9c12f6c9a9`.

The relevant paths are:

- `research/pro_review_20261010/full_data/`: original workbooks, complete extraction, selected records, exclusions and cell traces;
- `research/eex_abc_results_20261010/`: independent input audit, original A/B/C program and numerical results;
- `research/eex_robustness_20261010/`: extension protocol, core code and frozen result summary.

The source data remain subject to EEX's rights. Repository availability does not create a separate redistribution licence. The final author-approved data statement must explain any applicable access restrictions and the legal reproduction route. No credentials or private participant identities are required by the published analysis.

The completed experimental record reports 1,327 source date rows, 1,281 selected successful T3PA auctions and 46 exclusions. The excluded records consist of 38 other-product observations, five observations outside the selected reporting series and three cancelled auctions. Empty award fields on cancelled auctions were not imputed as zero. The analyst should reconstruct these conditions, not filter until a target sample size is achieved. The candidate CSV retains workbook, sheet and row provenance.

There are no zero reported standard deviations in the selected sample. Therefore B, the positive-standard-deviation version of A, has the same sample and the same fitted and resampled results. B is retained in the analysis record as the planned sample check. The main table displays only the distinct A and C estimates.

### S.2. Reproduction of the month-block procedure

The main resampling axis contains all 72 calendar months from January 2020 to December 2025. For a block length L, starting positions are drawn uniformly from the non-circular admissible starts. Each start contributes L consecutive original months; blocks are concatenated until 72 positions have been generated, and the excess is discarded. All auctions from a selected month are retained jointly, including all represented series.

Repeated months supply multiplicity weights to the original rows. Their original year–month fixed-effect labels are retained. Categories absent from a draw are omitted, rather than retained as zero dummy columns. Both the nuisance projection and the focal coefficient are re-estimated. Failed draws are logged without replacement draws; the reported completed runs have no failed bootstrap draw. A, B and C share each draw's sampled-month indices.

The primary block length is three months with 999 draws. One- and six-month sensitivity checks use 199 draws for A and C. The principal program uses a deterministic random-number stream initialized from the recorded seed and block length. This stream differs from an earlier team calculation; the principal manuscript reports the frozen program's intervals rather than selecting the more favourable realization. In particular, the principal ordinary-log slope interval includes one.

For the period analysis, the already explored split defines separate 36-month axes. Each half is resampled independently in three-month blocks, and all nuisance coefficients are re-estimated within that half. The same paired indices are used for A and C. The resulting differences are conditional on this approximation; dependence across the boundary is not fully represented. The 97.5% intervals for each transformed slope contrast are a limited Bonferroni-style sensitivity, not a correction for the entire history of exploratory selection.

For EU and PL subseries, one original month contains no selected observations. That empty month still occupies its position on the 72-month axis and never generates an invented auction. Months with a single observation contribute no net within-month information. The series and period estimates are not independent-study replications.

### S.3. Pooled block-length sensitivity

**Table S1. Frozen pooled percentile intervals**

| Spec. | Block months | Draws | β: 95% interval | θ: 95% interval |
| --- | --- | --- | --- | --- |
| A | 1 | 199 | [0.7807, 0.9833] | [0.5903, 0.7158] |
| A | 3 | 999 | [0.7506, 1.0384] | [0.5714, 0.7422] |
| A | 6 | 199 | [0.7350, 1.0292] | [0.5564, 0.7438] |
| C | 1 | 199 | [0.7907, 0.9714] | [0.5855, 0.7134] |
| C | 3 | 999 | [0.7627, 1.0143] | [0.5660, 0.7402] |
| C | 6 | 199 | [0.7503, 1.0090] | [0.5526, 0.7493] |

*Note:* All intervals are exploratory 95% percentile intervals using linear quantile interpolation. The three-month rows are the principal intervals, not additional replications. Small numbers of draws make the sensitivity endpoints approximate. These calculations do not establish exact coverage under arbitrary structural change.

### S.4. Influence diagnostics

**Table S2. Residual-correlation sensitivity to deletion**

| Deletion diagnostic | A: θ range / value | C: θ range / value |
| --- | --- | --- |
| One calendar month | [0.6419, 0.6656] | [0.6405, 0.6674] |
| One calendar year | [0.6058, 0.6981] | [0.6023, 0.6996] |
| One reporting series | [0.6019, 0.7120] | [0.6110, 0.7081] |
| One observation | [0.6467, 0.6569] | [0.6457, 0.6577] |
| Top 13 Cook-distance rows (joint deletion) | 0.6911 | 0.6930 |

*Note:* Bracketed entries in this table are ranges across deterministic deletions, **not confidence intervals**. The Cook-distance row is a jointly omitted set chosen within each specification for influence diagnosis. It is not a new primary sample or a data-cleaning rule. All main results retain 1,281 auctions. Statistical influence is not evidence that a record is erroneous.

### S.5. Reporting-series estimates

**Table S3. Within-series association**

| Spec. | Series | n | Residual df | θ [95% interval] |
| --- | --- | --- | --- | --- |
| A | EU | 840 | 764 | 0.6898 [0.6283, 0.7585] |
| A | DE | 275 | 198 | 0.5619 [0.4567, 0.6808] |
| A | PL | 166 | 90 | 0.8076 [0.6943, 0.8828] |
| C | EU | 840 | 764 | 0.6839 [0.6159, 0.7587] |
| C | DE | 275 | 198 | 0.5689 [0.4679, 0.6870] |
| C | PL | 166 | 90 | 0.8138 [0.7005, 0.8850] |

*Note:* Each series uses its own month effects and the fixed numeric controls. Intervals use 399 three-month block draws. EU, DE and PL are reporting series in the same allowance market, not three independent markets. Differences between point estimates do not constitute a formal between-series contrast test. PL has limited residual degrees of freedom.

### S.6. Algebraic check and rounding

Let V denote the reported auction-volume field. Define implied means B/N and V/S and the implied cover ratio B/V only for the algebraic calculation. Using these constructed quantities, residualized natural-log dispersion ratios equal residualized log standard deviations when the common control space includes the corresponding log totals and counts. The maximum residual discrepancies in the completed check are of order $10^{-14}$. This verifies arithmetic and projection code. It neither supplies an independent observed total award W nor authenticates V=W.

With reported values, the mean discrepancies against the implied values reach 0.5 quantity units, and the cover-ratio discrepancy reaches approximately 0.004994. Their consistency with displayed precision does not authenticate a historical rounding rule. The original reported fields are retained in the main regressions; constructed fields do not silently replace them. A log-one-plus ratio does not satisfy the natural-log additive identity.

If a common population and variance divisor were established, conventional moment identities could relate a dispersion ratio to single-auction concentration. Those conditions are not established here. The paper therefore does not compute a bidder-population HHI, infer annual concentration from average single-auction indices, or interpret its slope as a within-population allocation effect.

### S.7. Exploration and numerical provenance

The historical snapshot, research question and some results were seen before the supplementary protocols were recorded. The initial-freeze evidence is partial. The present draft uses post-exploration checks, not a preregistered design or an untouched holdout. Earlier values are not described as independent confirmations simply because an additional implementation reproduces them.

The completed experiments used a within-month projection implementation, with explicit-dummy and repeated-row crosschecks. The principal audit and the extension had separate bounded execution budgets; their fit counts are execution bookkeeping, not sample sizes or evidence strength. The manuscript-writing step only reads the existing outputs, verifies table arithmetic and formats tables and figures. It does not rerun either experiment.

An absolute residual-correlation reference of 0.10 was proposed after exploration. It is not an economic threshold or preregistered rule; the revised figures report the frozen estimates and intervals without that reference line.
