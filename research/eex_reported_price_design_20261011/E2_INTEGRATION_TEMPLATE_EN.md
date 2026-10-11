# Conditional integration text — NOT FITTED / NOT FOR SUBMISSION

This file is a prospective writing scaffold for the one amended analysis. It is not a new result and must not be pasted into the Results section as completed evidence. Existing v8/v8.1 estimates remain unchanged.

## Data and estimand (proposed Section 3.7 after row verification)

The supplementary pricing analysis uses deviations reported in German government auction reports, rather than quotes reconstructed from a native market feed. The archive concerns successful German EUA auctions during 2020–2025. The data-acquisition record reports 275 matched auctions and a conservative set of 240 auctions in 21 source quarters after removing 35 source-ambiguous records. These counts must be verified from the row-level inputs before estimation. The retained reference is generally the last best bid; four reported comparisons use the last trade. Neither quote age nor an independently authenticated UTC event clock is recovered from the reports.

The response is the signed percentage deviation as printed in the official table, expressed in basis points by multiplying the percentage-point value by 100. Printed zeros remain rounded observations. A monetary column titled “Absolute” is not treated as a mathematical absolute value. The empirical object is the reported comparison, not an executable midpoint discount. All conclusions must use the report's verified sign convention.

## Incremental association design

Let x denote log(1 + reported bid-quantity standard deviation / reported bid-quantity mean). The baseline includes log auction volume, log total and successful bidder counts, log cover ratio, the maximum-minus-minimum bid-price spread, log auction price, year effects and a last-trade indicator. The extension adds x on exactly the same observations. A separate German-project dummy is omitted because all observations belong to the same project. Award dispersion is not the focal variable in this pricing analysis.

All regressors describe the same completed auction; the specification does not identify a causal allocation effect or a forecast available before bidding. Price spread and auction price are included as descriptive conditioning variables, not instruments. A reported dispersion ratio is not relabelled as a verified common-population coefficient of variation.

## Uncertainty and scale

Uncertainty will be reported using quarter-clustered CV1/CR1 standard errors and exploratory t(G−1) intervals, accompanied by a single 999-draw null-imposed wild-cluster t test for the focal coefficient. The bootstrap assigns one Rademacher sign to each source quarter and re-estimates the extension from restricted baseline residuals. Its two-sided Monte Carlo p-value is distinct from the conventional t interval; no bootstrap confidence-set inversion is claimed. With approximately 21 quarters, cluster leverage and dependence across quarters remain material limits (MacKinnon, Nielsen and Webb 2023, Sections 4.3 and 5.3).

The fitted basis-point contrast is the focal coefficient times the observed interquartile range of residualized x, with the same fixed range applied to the coefficient interval. This is a conditional scale illustration, not a change in procurement costs. Incremental partial R-squared is secondary and cannot itself establish economic value.

## Result table skeleton (all fields pending actual execution)

| Specification | n / quarters | Focal coefficient | CV1 t interval | Conditional IQR contrast, bp | Primary WCR p |
|---|---|---|---|---|---|
| Signed reported gap, conservative sample | PENDING | PENDING | PENDING | PENDING | PENDING |
| Absolute reported gap, same sample | PENDING | PENDING | PENDING | PENDING | Not planned |
| Signed gap, no row-source flags | PENDING | PENDING | PENDING | PENDING | Not planned |
| Signed gap, best-bid references | PENDING | PENDING | PENDING | PENDING | Not planned |

The main and absolute-gap rows answer different questions; they must not be selected according to which is significant. No new estimate is available in this revision. No cross-year slope-stability or out-of-time forecast test is included in this bounded amendment.

## Discussion wording after real outputs

If a precise association is found, describe its direction and basis-point magnitude conditional on the stated controls and reference definition. If uncertainty is large, report that limitation rather than claiming no price information. If the data precisely exclude a substantively pre-specified scale, state only that bounded result. In every case, the extension remains Germany-specific and report-based, not causal evidence of efficiency, strategic conduct, procurement savings or matched-bidder inequality.

Reference: MacKinnon JG, Nielsen MØ, Webb MD (2023) Cluster-robust inference: A guide to empirical practice. Journal of Econometrics 232:272–299. DOI: 10.1016/j.jeconom.2022.04.001.
