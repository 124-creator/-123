# Supplementary evidence: composition weighting and a 2026 time extension

**Status.** These analyses supplement, rather than replace, the frozen 2020–2025 manuscript. The historical question and earlier results had already been inspected. The new protocol was recorded before the present weighted fits, not before the historical research process. This is exploratory evidence, not retrospective preregistration. The original A/B/C sample and intervals remain unchanged; A and B were identical.

## E1. Composition-standardized period association

The early and late groups contain 643 and 638 successful EUA auctions. We estimate one unpenalized logistic model for late-period membership from an intercept, standardized log auction volume, total bidders, successful bidders and cover ratio, their squared terms, reporting-series indicators and month-of-year indicators. Neither dispersion measure, prices, year nor year–month identifiers enter this model. The resulting early and late weights are, respectively, estimated e and 1−e. This descriptive overlap construction draws on Li, Morgan and Zaslavsky (2018). It is not a treatment-effect design: period membership and simultaneous auction outcomes have no randomized interpretation.

The four original log controls, reporting-series effects and original year–month effects are re-estimated separately within each period using weighted least squares. The correlation of the two weighted residuals defines theta. An intercept is included through the month effects. The weighted late-minus-early correlation difference is the estimand of this supplemental comparison, not a replacement for the earlier manuscript's primary slope contrast.

Each main draw independently resamples three-month blocks within the two 36-month halves. The period-membership model and all outcome projections are refitted in each of 999 draws. Transformations share draw indices; failed draws are retained without replacement. One- and six-month checks use 199 draws. These procedures do not remove the exploratory selection history or fully model cross-boundary dependence. Individual 97.5% intervals provide only a limited two-comparison sensitivity, conditional on their approximation.

### E1.1 Results and diagnostic limits

| Transformation | Weighted early theta | Weighted late theta | Difference | 95% interval | 97.5% interval |
|---|---:|---:|---:|---|---|
| A | 0.5703 | 0.7675 | 0.1971 | [0.1084, 0.2910] | [0.0947, 0.3029] |
| C | 0.5649 | 0.7586 | 0.1937 | [0.0982, 0.2843] | [0.0847, 0.3051] |

The unweighted differences are 0.2297 and 0.2305. Weighting reduces these point differences by 0.0326 and 0.0368, but the corresponding paired 95% intervals are [−0.1349, 0.0802] and [−0.1449, 0.0797]. Thus the analysis does not establish a statistically discernible weighting-induced reduction or a causal fraction attributable to composition. Both weighted-difference 97.5% intervals are positive but include 0.10, a post-exploration descriptive reference rather than an economic or publication threshold.

All fitted model terms have weighted mean differences below 1.6×10⁻¹⁵; the selected squared terms also balance the corresponding second moments. Weight-concentration effective sample sizes are 586.55 and 614.75, not counts of independent temporal observations. However, **auction-volume distributions remain different**: the empirical KS distance is 0.2810 before and 0.2908 after weighting. Other weighted distances are 0.0364 for total bidders, 0.0201 for successful bidders and 0.0579 for coverage. The volume result exceeds the protocol's 0.10 diagnostic reference. Balancing selected means and variances has not balanced every distributional feature. No additional spline, trimming rule or weight model was chosen to conceal this failure.

The defensible finding is therefore narrower than full composition invariance: a positive period difference remains after standardizing selected composition moments. It does not exclude effects associated with unbalanced distributional shape, unidentified statistical populations, unobserved composition or common determinants. Balancing and partial-regression calculations do not identify a change in allocation efficiency or within-bidder inequality.

## E3. A new-time re-estimation in January–September 2026

An official EEX production workbook was downloaded on 10 October 2026, with 72,742 bytes and SHA-256 `54e6fb649872d229333adb29b62a3ff5b7fddd7393facc047050fb8f87a1bf3d`. The required 13 literal field labels match the historical extraction schema. Of 173 dated rows through 9 October, seven October observations fall outside the pre-specified complete-month cutoff. The resulting 166 successful T3PA auctions comprise 111 EU, 35 DE and 20 PL reports, cover all nine months and have unique dates. Dates and eligibility were not selected after estimating the 2026 relationship.

| Transformation | Slope beta | Residual correlation theta | Diagnostic 95% interval for theta |
|---|---:|---:|---|
| A | 1.3137 | 0.8494 | [0.8123, 0.9149] |
| C | 1.2375 | 0.8350 | [0.7832, 0.9156] |

The same equal-auction-weighted specifications are re-estimated with 2026 year–month and series effects. Consequently this is not prediction by a frozen historical model, nor is it an independent-market replication. There are only nine months and seven possible contiguous three-month source blocks. Although all 999 planned draws succeed, these intervals are fragile short-axis diagnostics, not evidence of precise confirmatory coverage. Resampling medians also differ from the point estimates. No formal contrast between 2026 and the 2023–2025 period was pre-specified or performed, so higher 2026 point estimates are not described as a statistically established continuation of the earlier increase.

The runner processed the raw file, preserved its hash and output metadata, and removed the temporary raw file without republishing it. Local readback verified code hashes, all stored percentile endpoints, paired draw identities and the residual-correlation-squared identity. This is not a second independent parsing of the 2026 workbook. Identical labels and byte identity do not certify unchanged standard-deviation populations or first-release versions. Access to an exact archived source or a lawfully held copy remains necessary for future raw-data reproduction; later downloads from the dynamic annual URL must not be assumed identical.

## E2. External price validation remains incomplete

The proposed economic extension requires a per-auction secondary-market reference with a matching allowance product and a documented pre-close reference time. The supplied workbooks' auction and bid-price columns do not provide that reference. The attempted official report routes returned access failures. No daily closing price, monthly average, chart-digitized value or other surrogate was substituted, and no price regression was estimated. E1 and E3 improve the description and temporal reach of the quantity relationship, but do not substitute for this external economic validation.

## Computational provenance

The historical input was reconstructed from six workbooks and reconciled to 1,327 dated rows, 1,281 candidates and 46 exclusions. The standard-library XML reader matched 17,251 numeric cells and 78 source labels; 11 input hashes were unchanged. E1 used 12,582 core requests plus 134 real-data numerical-validation requests, including failed validation attempts; E3 used 2,000 requests. These counts describe computation rather than independent evidence. E3's request cap was corrected from an arithmetic underestimate before obtaining 2026 data. Eighteen distinct synthetic tests passed in normal and optimized modes.

An initial BFGS cross-check lost precision on a fixed resample. It was retained in the record and replaced only as a validation implementation by an equivalent orthonormal-coordinate trust-exact optimizer, without changing the primary model or relaxing its acceptance tolerances. Seven fixed cases then agreed in slopes and correlations to approximately 6.3×10⁻¹². This is numerical validation on the same data, not an additional economic replication.

**Reference:** Li F, Morgan KL, Zaslavsky AM (2018). Balancing Covariates via Propensity Score Weighting. Journal of the American Statistical Association 113(521):390–400. https://doi.org/10.1080/01621459.2016.1260466
