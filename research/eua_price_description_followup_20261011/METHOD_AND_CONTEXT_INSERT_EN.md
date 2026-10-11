# Descriptive context and source-definition note for the price extension

This is a post-estimation descriptive addition to the fixed results at fccd471de96548bd781c59aced4a59435aae08ac. It neither changes the analysis sample nor introduces another regression. DESCRIPTIVES.csv contains the exact machine-readable table; quantiles use linear interpolation (type 7), and reported standard deviations use n−1.

## Suggested descriptive paragraph

Across the 240-auction primary sample, the official-reported signed deviation averages -2.80 basis points, with a median of -7.00, an interquartile range from -29.00 to 17.25, and a sample standard deviation of 46.34 basis points. Negative deviations account for 142 observations (59.17%), positive deviations for 92 (38.33%), and reported zeros for 6 (2.50%). A reported zero denotes equality at the publication's displayed precision; it does not establish exact equality of unrounded prices or absence of trading. The absolute reported deviation has a mean of 33.51 basis points and a median of 25.00, with quartiles of 11.00 and 46.00 basis points. These unconditional summaries provide context for, but are not estimates of, the conditional fitted difference of −14.51 basis points associated with an observed interquartile range of the transformed dispersion indicator.

## Baseline and inference wording

The price-level control is the logarithm of the same-auction clearing price, not an independently observed pre-auction secondary-market price. Together with participation, successful bidder counts and demand coverage, it defines a contemporaneous descriptive conditioning set. The exercise does not identify a total causal effect. Keep the CR1 t-based intervals, the null-imposed wild-cluster p-value, and the mean-centred delete-quarter jackknife interval separately labelled. With 21 primary quarters and 18 quarters in the no-row-flag subset, cross-quarter dependence is not automatically resolved by resampling.

## Source definition and remaining boundary

The reports describe their observations as deviations of auction clearing prices from a secondary-market reference. A targeted check of native method text in the 24 held reports did not locate an explicit subtraction-and-denominator equation; the early and late method sections confirm the trade/best-bid reference convention but do not resolve that mathematical definition in the examined passages. The analysis therefore retains the original signed reported percentages without reconstructing a reference price from rounded entries. Its result is described as a lower official-reported signed deviation, not as a newly authenticated widening discount. This wording boundary does not turn the completed regression back into an unperformed experiment.

## Year influence

Deleting 2022 changes the focal coefficient from -78.72 to -45.12, a 42.7% reduction in its absolute magnitude. This is a comparison of two fitted coefficients, not a decomposition assigning a percentage contribution to that year. The deletion diagnostic reports point estimates only and does not establish that the estimate excluding 2022 is statistically significant. The absolute-deviation confidence interval includes zero; it neither supports improved auction efficiency nor proves a zero relationship.

No entire Word manuscript is represented as integrated by this addition. Retain the original quantity-analysis sample and the matched German price-analysis sample as separate empirical relationships; no allocation-mediated price mechanism has been tested.
