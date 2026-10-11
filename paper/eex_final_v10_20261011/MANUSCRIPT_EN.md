# Quantity dispersion and reported price deviations in European carbon auctions

Conditional associations and historical scope

Zhongfei Tian · Xiang Wang

Zhengzhou University of Aeronautics, Zhengzhou, Henan, China

Corresponding author: Zhongfei Tian · 15517837680@163.com

### Abstract

Public carbon-auction reports summarize bidding, allocations and prices, but marginal statistics do not establish whether quantity dispersion contains distinct information. We examine two conditional relationships using European Union Allowance auctions: bid–award dispersion in 1,281 successful auctions during 2020–2025, and reported price deviations in a matched sample of 240 German auctions. The quantity ratios have residual correlations near 0.65 after controlling for scale, participation and time effects. Their association is stronger in 2023–2025 despite lower marginal medians, and the period contrast remains positive after standardizing selected composition moments. In the German sample, greater bid dispersion is associated with a lower official-reported signed price deviation beyond demand coverage, bidder counts, submitted-price range, the same-auction clearing price and year effects. An observed interquartile range of transformed bid dispersion corresponds to a fitted difference of −14.51 basis points (exploratory quarter-clustered 95% interval: −23.00 to −6.01). Two predefined source subsets retain the negative direction. However, the absolute-deviation interval includes zero and omitting 2022 substantially attenuates the coefficient. The results distinguish shared quantity variation, the conditional location of reported price comparisons and distance from the reference. They establish report-level associations with historical and measurement limits, rather than causal allocation effects, improved pricing efficiency or forecasting value.

Keywords: European Union Allowances; primary auctions; quantity dispersion; reported price deviations; measurement; temporal heterogeneity

JEL classification: D44; C13; Q58

## 1 Introduction

Carbon auctions make the allocation of allowances observable through a set of public quantities, participation counts and prices. These reports contain more than a clearing price, yet the economic information in their different fields need not coincide. A count of participants describes the breadth of recorded participation; total submitted quantity describes aggregate demand; and a dispersion statistic describes variation in the reported quantities. Official reporting publishes these dimensions side by side, while the European Securities and Markets Authority (ESMA) separately monitors participation and concentration (European Commission 2024; ESMA 2025). The empirical question is whether reported quantity dispersion adds a distinct conditional description once scale and participation have been made explicit.

This question has two parts. Awards originate in submitted bids, so a positive relationship between bid and award dispersion is plausible. Neither its strength nor its stability is determined by that observation. Separately, a quantity statistic may be related to a price comparison even if it is strongly related to another quantity statistic. We therefore study, first, the conditional association between the reported dispersion of bids and awards and, second, whether reported bid dispersion is associated with official price deviations beyond conventional auction characteristics. The second analysis extends the set of outcomes; it does not test whether awards mediate a bid-to-price mechanism.

The analysis concerns European Union Allowances (EUAs). Its historical quantity sample comprises 1,281 successful auctions in the EU, DE and PL reporting series of the European Energy Exchange (EEX), covering 2020–2025. These series belong to one allowance market. The matched price analysis uses 240 German auctions in 21 quarters for which the official reported comparison passes fixed source restrictions. Thus the price observations are a subset of the historical archive, not an additional independent sample of 240 auctions. A separate 2026 quantity sample is used only to examine the temporal scope of the original quantity relationship.

The price specification distinguishes dispersion of quantities from the range of submitted bid prices. This distinction is important because existing auction-price research already considers participation, demand coverage and submitted-price variation (Bosco 2023). Our baseline retains these dimensions, adds the same-auction clearing-price level and year effects, and compares an extension containing the bid-dispersion ratio on exactly the same observations. The comparison asks about incremental conditional association in completed auction reports. It is not an exercise in forecasting an auction before bids arrive, and it does not treat the included characteristics as exogenous determinants.

Two principal findings emerge. The quantity ratios have residual correlations close to 0.65 under both transformations. In the German price sample, an interquartile range of transformed bid dispersion corresponds to a fitted signed-deviation difference of −14.51 basis points. The price result is not equivalent to closer alignment with the reference: the absolute-deviation interval includes zero, and its point estimate is positive. The signed coefficient also becomes materially smaller when 2022 is omitted. We report these qualifications alongside the main estimate rather than treat every sensitivity calculation as evidence of universal stability.

The historical quantity evidence adds a further distinction. The later period has lower marginal dispersion ratios but a stronger conditional relationship between bids and awards. The period contrast remains positive after balancing selected observed composition moments, although the auction-volume distributions remain unequal. The contribution is therefore a measurement-explicit characterization of quantity and price information in the reports, with a clear separation between levels, co-variation and signed price location. It extends beyond documenting a positive bid–award correlation, but does not introduce a new estimator, authenticate bidder-level concentration or establish an operational benefit.

The study is retrospective. The historical archive and earlier findings were inspected before supplementary checks; the price specifications were fixed after source inspection and before the first price fit. All inferential statements retain that exploratory status. The article is organized around the economic questions rather than the order in which checks were conducted. Section 2 develops the institutional and measurement context. Section 3 describes the samples, and Section 4 defines the estimands. Section 5 presents the quantity and price findings together; Section 6 examines historical scope and sensitivity. Sections 7 and 8 discuss the information added and conclude. Online Resource 1 supplies implementation details and supplementary evidence.

## 2 Institutional setting and economic questions

### 2.1 Allocation, participation and reported quantities

EEX describes its emissions auctions as single-round, sealed-bid, uniform-price auctions. Bids are ranked by price, successful orders pay the clearing price, and marginal execution can be partial. Participants may bid on their own account or on behalf of clients (EEX n.d.). A reporting participant therefore need not be the final installation using allowances for compliance. This distinction matters for the quantities and counts studied here, which cannot be converted into client-level demand without additional information.

Allowance auction design matters for rents and allocation as well as the clearing price (Cramton and Kerr 2002). Multi-unit auction theory links bidding incentives and demand reduction to allocation outcomes (Ausubel et al. 2014). These considerations motivate attention to quantity distributions. Our data contain public aggregate moments rather than valuations or participant-specific bid schedules, so they support a description of quantity co-variation, not a test of strategic demand reduction.

### 2.2 What the report fields can distinguish

Auction size, participation and quantity dispersion are related but different objects. Even when aggregate submitted quantity and the number of participating bidders are fixed, that total can be distributed more or less unevenly across the reported observations. Consequently, a dispersion field is not determined by those two totals alone. This elementary distinction motivates conditioning on totals and counts rather than treating the reported dispersion ratio as a substitute for demand coverage. It does not identify the participants underlying each reported moment, an issue addressed explicitly in Section 3.

Quantity and price dispersion must also be separated. The highest and lowest submitted prices describe the span of prices in the bid book, but do not state how much quantity is attached to different prices. Conversely, an auction-level quantity standard deviation does not locate bids relative to the clearing threshold. A relationship between quantity dispersion and a reported price comparison is therefore a testable empirical association, not an accounting identity. Aggregate moments are insufficient to recover the bid schedule, so the analysis cannot distinguish strategic demand reduction from heterogeneous demand, intermediation or common market conditions.

The empirical design separates two questions that are sometimes conflated in interpreting price comparisons. A signed outcome concerns the location of the reported comparison, whereas its absolute value concerns distance from zero. A shift in the signed outcome could move an observation closer to or further from the reference, depending on its initial position. With both positive and negative observations present, a coefficient in a signed regression cannot establish improved alignment. We retain both outcomes, with the signed outcome designated as primary before the first price fit. This distinction is necessary for interpretation regardless of which estimate is statistically distinguishable from zero.

The quantities also need not have a single historical relationship. Differences in auction composition, reporting conventions or unobserved demand conditions may change a cross-auction projection. A pooled coefficient consequently summarizes a selected archive, not a permanent allocation rule. The period, composition and new-time analyses examine different aspects of this scope. They are not instruments for one another and do not form a causal explanation of the price result. These are interpretive implications of the design, not directional hypotheses retrospectively presented as preregistered predictions.

### 2.3 Relation to auction-price and measurement research

Bosco (2023), first published online in 2022, studies EUA auction prices and returns with GARCH specifications. Participation, demand coverage and the maximum-minus-minimum submitted bid price enter its analysis. That price range is distinct from quantity dispersion and is therefore included in our fixed price baseline. Our extension concerns a reported auction-to-secondary-market comparison, not price volatility or a new test of whether auction characteristics matter in general. Niu and Liu (2024) instead forecast EUA futures volatility; no forecasting contest is conducted here.

Otsubo (2026) studies intraday price discovery between futures and an exchange-traded fund (ETF), together with a daily auction–futures–ETF comparison aligned to 16:00 UK time. We use the price deviations already reported by the German Emissions Trading Authority (DEHSt 2020–2025), rather than reconstructing synchronous native quotes or estimating cross-venue information shares. The source and timing distinctions prevent either analysis from being treated as a direct replication of the other.

Official reporting provides the measurement context. The Commission distinguishes individual-auction means from monthly aggregates and describes bid and award means using participating and successful bidders, respectively (European Commission 2024). ESMA (2025) separates participation from concentration indicators. The DEHSt quarterly reports provide the German price comparisons used in our extension. These dimensions are established reporting objects. The contribution is their conditional empirical relationship, not the introduction of the fields or a claim that official reporting has used them incorrectly.

Two measurement cautions shape the design. Shared ratio components can affect regression relationships, so normalizing by a mean is not a substitute for making totals and counts explicit (Kronmal 1993). In addition, association between observed indicators does not identify a latent common factor. The multiple-proxy framework of Meijer et al. (2025) makes the identification and normalization conditions for that different task explicit. We impose no such factor model. The analysis retains the original report fields, examines the specified transformations and control sets, and uses a separate algebraic check to explain the role of constructed denominators.

The measurement literature offers a useful distinction between comparing indicators and relating them to another outcome. Hackl et al. (2026), for example, assess search-based product-differentiation measures using product attributes and price relationships, while retaining a non-causal interpretation. Our use of reported auction moments is narrower: it does not validate a new measure of a latent characteristic. The German price analysis instead asks whether an established report field has a conditional association with a different reported outcome, beyond the stated baseline.

## 3 Data, samples and measurement

### 3.1 Historical quantity archive and reported measures

The data are six EEX annual primary-auction workbooks for 2020–2025, preserved in a fixed research snapshot. Extracting every dated row yields 1,327 records. The sample retains product code T3PA, the EU/DE/PL reporting series and an explicit successful status. The rule excludes 38 other-product records, five records outside the specified series and three cancelled auctions. It leaves 1,281 unique auctions between 7 January 2020 and 15 December 2025, covering all 72 calendar months. Table 1 gives their distribution. The three series belong to the same allowance market and are not independent-market replications.

Table 1 Sample composition by year and reporting series

| Year | EU | DE | PL | Total |
| --- | --- | --- | --- | --- |
| 2020 | 139 | 46 | 24 | 209 |
| 2021 | 132 | 45 | 46 | 223 |
| 2022 | 142 | 46 | 23 | 211 |
| 2023 | 143 | 47 | 24 | 214 |
| 2024 | 142 | 46 | 24 | 212 |
| 2025 | 142 | 45 | 25 | 212 |
| Total | 840 | 275 | 166 | 1281 |

Note: Counts refer to successful T3PA auctions satisfying the stated series restriction. Cancelled auctions and other products are not recoded as zero outcomes. The first three years contain 643 auctions and the final three contain 638.

The selected sample has complete numeric fields for the fixed measures and controls. Both reported means are positive; neither standard-deviation field contains a zero. No auction is removed because its dispersion ratio is large or small. There is one selected auction per distinct date, but observations can remain dependent over time. Selection on successful completion defines the population of interest; the analysis does not describe cancelled auctions or latent demand.

Each record retains its source workbook, sheet and row. The completed source audit reconciled the exclusions and compared the numeric extraction with a separate XML-reading route. The audit establishes traceability of the supplied snapshot, not the first historical release of every field. Online Resource 1, Section S2, records the cell counts and verification scope.

Let μtb,stb denote the reported mean and standard deviation of bid volume, and μtw,stw the corresponding reported moments of volume won. Define

rtb=stbμtb,  rtw=stwμtw.(1)

We call these reported dispersion ratios. The original labels refer to volume per bidder. Nevertheless, the population underlying each standard deviation and its variance divisor have not been conclusively matched to the paired mean throughout the archive. The ratios are therefore not interpreted as verified coefficients of variation for an identical population before and after allocation. This restriction affects the economic interpretation, not the arithmetic definition in (1).

For descriptive context, Table 2 reports the two dispersion ratios (reported standard deviation divided by reported mean), the conditioning variables and total bid volume. All summaries give each auction equal weight. Volumes are displayed in millions of tCO2; ratios and counts retain their original scales. Quartiles use linear interpolation. No winsorization, trimming or additional sample restriction is applied.

Table 2 Descriptive statistics of the successful-auction sample

| Variable | Mean | Q1 | Median | Q3 | Min. | Max. |
| --- | --- | --- | --- | --- | --- | --- |
| Bid ratio rb | 1.404 | 1.202 | 1.387 | 1.579 | 0.847 | 2.622 |
| Award ratio rw | 1.422 | 1.215 | 1.399 | 1.598 | 0.443 | 2.707 |
| Cover ratio R | 1.825 | 1.540 | 1.740 | 2.030 | 1.010 | 3.780 |
| Auction volume V | 2.675 | 2.296 | 2.651 | 3.245 | 0.970 | 6.399 |
| Submitted volume B | 4.717 | 3.986 | 4.736 | 5.321 | 1.937 | 12.899 |
| Total bidders N | 22.663 | 20 | 23 | 25 | 12 | 31 |
| Successful bidders S | 16.878 | 14 | 17 | 20 | 3 | 27 |

Note: All rows use 1,281 auctions. V and B are in million tCO2, N and S are bidder counts, and the three ratios are dimensionless. B maps to the source field “Total Amount of Bids” in the workbook’s volume section, not to auction revenue. Q1 and Q3 are the 25th and 75th percentiles. These are marginal descriptive statistics, not conditional estimates or bidder-level distributional comparisons.

The separate sample medians are 23 participating bidders, 17 successful bidders, 2.651 million tCO2 of auction volume and a cover ratio of 1.740; these need not occur in one observed auction. Median bid and award ratios are 1.387 and 1.399. Figure 1 shows the period-specific medians and interquartile ranges, with full summaries in Online Resource 1, Table S5. These marginal quantities are distinct from the conditional correlations below.

Fig. 1 Marginal reported dispersion ratios by historical period; diamonds denote auction-level medians and horizontal segments extend from the 25th to the 75th percentile. Each early-period row contains 643 auctions and each late-period row 638. These segments describe the middle half of the observations; they are not confidence intervals or paired-bidder comparisons. The figure reuses the descriptive statistics in Online Resource 1, Table S5

### 3.2 Matched German price comparisons

The price extension pairs the EEX quantity fields with comparisons printed in DEHSt quarterly reports for 2020–2025. Source reconciliation identifies 275 German successful auctions across all 24 quarters. The prefit source restrictions quarantine 35 observations for reference-footnote or date inconsistencies, leaving 240 auctions in 21 quarters. Of these, 236 use a last-best-bid reference and four a last-trade reference. The predefined no-row-flag subset contains 203 auctions in 18 quarters. These are subsets of the historical archive, not additional auctions or an independent market.

Source eligibility is kept separate from statistical influence. The price exclusions concern unresolved report footnotes or a conflicting date, rather than the size or sign of a fitted residual. Nevertheless, a source-selected sample need not represent all German auctions, let alone the EU and PL series. The 203-observation and best-bid subsets are further restrictions of the same data. Their agreement is informative about those specified restrictions, but cannot establish equivalence of reference quality or replace observations excluded by the source contract. Online Resource 1, Section S12, records the restrictions by source quarter.

The signs and units are preserved rather than reconstructed. In particular, the analysis does not divide a reported euro difference by an inferred price to recover a formula that was not located in the examined source text. Signed percentage points are converted only to basis points. This transparent transformation keeps the analysis reproducible at publication precision while leaving the original sign convention as an interpretation boundary. The regression thus describes a lower official-reported signed deviation; it does not relabel that finding as a larger auction discount.

Table 3 summarizes the price outcome on its reported scale. In the primary sample, the signed deviation has a mean of −2.80 and median of −7.00 basis points, with quartiles −29.00 and 17.25. There are 142 negative observations (59.17%), 92 positive observations (38.33%) and six reported zeros (2.50%). The absolute deviation has a mean of 33.51 and median of 25.00 basis points. These unconditional summaries provide a scale for reading the fitted contrasts; they are not estimates of the conditional relationship. The corresponding descriptions for the two source subsets appear in Online Resource 1, Table S11.

Table 3 Descriptive context of German official-reported price deviations

| Outcome | Mean | Median | Q1–Q3 | Range | SD |
| --- | --- | --- | --- | --- | --- |
| Signed deviation | −2.80 | −7.00 | [−29.00, 17.25] | [−174.00, 171.00] | 46.34 |
| Absolute deviation | 33.51 | 25.00 | [11.00, 46.00] | [0.00, 174.00] | 32.06 |

Note: Both rows use 240 auctions in 21 quarters. Values are basis points on the official reported percentage scale. SD denotes the sample standard deviation with divisor n−1; quartiles use linear interpolation. Signed observations comprise 142 negative, 92 positive and six printed-zero values. A printed zero is not a no-trade state or proof of equality of unrounded prices. The absolute outcome is the modulus of the reported signed outcome, not a reinterpretation of an original column labelled Absolute.

### 3.3 Sample scope and the additional time segment

The primary quantity sample and the price subset serve different purposes. The former offers broad coverage across the three reporting series; the latter adds a distinct outcome at the cost of narrower geographic and source coverage. The separate January–September 2026 quantity exercise contains 166 auctions in nine months and is not merged with either historical sample. Its analysis re-estimates the relationship, including new year–month effects, rather than carrying a historical forecasting rule into the future. The 22 separately acquired German price observations from 2026 remain unused.

## 4 Empirical strategy

### 4.1 Quantity projections and standardized association

Specification A sets xt=log1+rtb and yt=log1+rtw. The main conditional projection is

yt=βxt+γ′zt+αjt+δmt+ut,(2)

where jt denotes the reporting series, mt the original year–month, and zt=logRt,logVt,logNt,logSt′. Here R is the reported cover ratio, V reported auction volume, N total bidders and S successful bidders. The submitted-volume field B, used in the denominator audit and Table 2, is labelled “Total Amount of Bids” in the source workbook; it is not an additional regressor in (2). All observations have equal weight. The pooled full design has rank 79 and 1,202 residual degrees of freedom.

The fixed supplementary measurement comparison contains A, a positive-standard-deviation version of A labelled B, and a natural-log version C on the same positive sample. Since all selected standard deviations are positive, A and B are identical. B is retained in the reproduction record as a sample-eligibility check rather than a separate result. C uses xt=logrtb and yt=logrtw on exactly the same 1,281 rows. No constant is added to a zero standard deviation.

All variables concern the same completed auction. In particular, the cover ratio and successful-bidder count are simultaneous outcomes, not instruments or inputs known before bidding. Equation (2) is an equal-auction-weighted descriptive linear projection for the selected archive. Its coefficient depends on the conditioning set and on the distribution of those auctions. To examine dependence on those conditions, we also report fixed effects alone and fixed effects plus logV and logN. These models answer related, but not identical, conditional questions. Year–month effects account for monthly levels; they do not absorb every daily common shock.

Reported means are numerically consistent with total submitted volume divided by N and reported auction volume divided by S, to the archive’s displayed precision. This creates an explicit denominator structure. Under natural logs, constructed means and a constructed cover ratio yield additive identities that disappear after projection on the corresponding totals and counts. The log-one-plus transformation does not have that property. Online Resource 1 derives and checks these identities, keeping constructed fields separate from the reported fields used in (2).

Let Z contain the nuisance regressors and fixed effects in (2), and let MZ denote the residual-maker for that space. With x=MZx and y=MZy, the coefficient and standardized association are

β=x′yx′x,  θ=βsxsy.(3)

This is the partial-regression representation (Lovell 1963). In the present equal-weight, single-added-regressor setting, θ is the sample correlation of the two residuals. The partial coefficient of determination satisfies

Rpartial2=SSEZ−SSEZ,xSSEZ=θ 2.(4)

These are complementary scales for the same association, not independent pieces of evidence. The residual correlation is symmetric in the two indicators; placing award dispersion on the left of the regression does not establish a direction of transmission. Pooled and subperiod correlations use their respective fitted control spaces and variances, so a change in correlation need not be a change in a structural parameter. We also report the fitted transformed-response contrast corresponding to an observed interquartile range of residualized x. It is a scale illustration along the fitted partial regression, not an intervention or an expected procurement gain.

The principal uncertainty calculation uses a month-block resampling design for dependent observations, within the general class discussed by Lahiri (2003). It resamples non-circular blocks of three consecutive calendar months. Starting months are drawn with replacement; blocks are concatenated and truncated to a 72-month axis. All auctions in a selected month are retained jointly. Repeated months increase row multiplicities and retain their original fixed-effect labels. The entire conditional projection is re-estimated for each of 999 draws. A and C share the draw indices. One- and six-month blocks, with 199 draws each, provide bounded sensitivity checks. Intervals are percentile intervals with linear quantile interpolation.

We examine influence by deleting each observation, month, year and series, and by jointly omitting the 13 largest-Cook-distance observations under each specification (Cook 1977). These diagnostics do not redefine the main sample. Within-series models retain their own monthly effects; empty months retain their positions on the 72-month resampling axis. Reduced-control and within-series intervals use 499 and 399 three-month block draws, respectively.

### 4.2 Price-deviation projection and matched baseline

Let d denote the official signed numeric percentage deviation multiplied by 100, so that its unit is a basis point. A printed −0.07% becomes −7 basis points. The study does not infer an unreported denominator or recover a native reference price from rounded entries. Reported zeros remain zeros at publication precision, not missing values, no-trade indicators or proof of exact unrounded equality. The focal regressor x is the same log-one-plus bid-dispersion ratio used in specification A. We fit the descriptive projection

dt = a + κ xt + λ′ct + ηY + et(5)

where Y denotes the calendar year of auction t and c contains log auction volume, log total and successful bidder counts, log reported coverage, the highest-minus-lowest submitted price in euros, log same-auction clearing price, and a last-trade indicator when it varies. The year effects differ from the year–month effects in the quantity analysis. The full primary design has rank 14 and 226 residual degrees of freedom. Its baseline omits only x on exactly the same rows. No reported award-dispersion term is used to infer a mediation channel. All controls describe completed auctions; in particular, clearing price and coverage are simultaneous outcomes.

Each element of the price baseline addresses a distinct descriptive dimension: auction volume describes supply scale; bidder counts describe recorded participation and success; coverage describes submitted demand relative to supply; and the submitted-price range captures variation in offered prices. The clearing-price level and year effects condition on contemporaneous level and annual differences. None of these controls measures the full bid schedule or eliminates simultaneity. In particular, including the clearing price, a component of the underlying comparison, restricts the coefficient to association conditional on that price level; it cannot be read as the total response of the clearing price to dispersion.

Uncertainty is reported using a finite-sample-corrected quarter-cluster covariance estimator (CR1) and t(G−1) 95% intervals, with G equal to the number of observed quarters. The primary coefficient also receives one null-imposed wild-cluster t test with 999 Rademacher draws. A mean-centred delete-quarter jackknife (CV3J) and six fixed leave-one-year-out estimates assess influence. These procedures are related checks on the same data, not independent confirmations; cross-quarter independence and small-cluster calibration remain assumptions (MacKinnon et al. 2023). The CR1 interval is not a bootstrap interval.

The locked secondary specifications use the absolute deviation on the same 240 rows, the signed deviation on the 203 no-row-flag observations, and the signed deviation on the 236 best-bid observations. The main scale illustration is κ times the observed interquartile range of x, holding the fitted conditioning set fixed. A contrast using the interquartile range of residualized x is retained separately. Neither is a feasible intervention or monetary return. The final code and specifications were fixed before the first price fit but after inspection of the source data. Twenty-two separately acquired German price observations from 2026 were not fitted or merged into this analysis.

The price analysis uses quarters as its uncertainty clusters, not as 21 independent experimental replications. Cluster methods allow dependence within the chosen groups but still rely on an appropriate approximation across groups. We therefore retain the CR1-t interval, the restricted test and the delete-quarter calculation as separately labelled diagnostics. Their agreement cannot demonstrate that cross-quarter dependence is absent. No reported p-value accounts for all earlier choices in the research programme, and changing the order of presentation here does not change any analysis from exploratory to confirmatory.

### 4.3 Historical scope and composition comparisons

The historical comparison divides 2020–2022 from 2023–2025, a split already present in earlier exploration. The two samples contain 643 and 638 observations, and all nuisance coefficients are estimated separately. Each 36-month half is independently resampled in three-month blocks for 999 paired draws, with common indices across transformations. The protocol’s primary contrasts are late-minus-early slopes, Δβ = βlate − βearly. Each transformation receives a 97.5% percentile interval as a Bonferroni-style nominal family-95% sensitivity calculation, conditional on adequate individual interval approximations. We also display the previously computed secondary contrasts Δθ = θlate − θearly with their exploratory 95% intervals. These are direct comparisons of standardized association; a slope-difference interval does not test a correlation difference. The secondary intervals are neither family-adjusted over the two transformations nor replacements for the originally designated primary contrasts.

We use descriptive overlap weights to emphasize auction characteristics represented in both historical periods. Following Li et al. (2018), one unpenalized logistic model predicts late-period membership from an intercept, the four pooled-standardized log controls, their squared terms, reporting-series indicators and month-of-year indicators. Neither dispersion measure, price, year nor specific year–month enters this model. Early weights are the fitted late-period probabilities; late weights are one minus those probabilities. Coverage and successful participation remain joint auction outcomes. The weights standardize selected observed moments and are not a causal treatment design.

Within each period, both transformed indicators are projected on the original controls and year–month effects by weighted least squares. We compute their weighted residual covariance and divide by the product of the weighted residual standard deviations, using the same weights throughout. The supplemental contrast is the late-minus-early difference in that correlation. Every block draw refits the period-membership model and both outcome projections. The main calculation uses 999 three-month draws, with 199 draws each for one- and six-month sensitivity checks. Individual 97.5% percentile intervals address the two weighted contrasts only as a limited multiplicity sensitivity. Weight concentration, fitted-term balance, distribution distances and the paired change from equal weighting are reported together. No outcome-dependent trimming or alternative weight-model search is used.

A nine-month axis provides only seven non-circular three-month source blocks. Following the initial 999 draws, a post-result diagnostic enumerates the finite non-circular and circular resampling distributions and deletes each month in turn. Non-circular sampling underweights endpoint months; circular sampling balances their expected inclusion but joins September to January artificially. The resulting ranges are short-axis diagnostics, not certified coverage intervals. Original results remain available in Online Resource 1, Section S11, and no formal difference between 2026 and earlier years is tested.

### 4.4 Research sequence and disclosure

The historical archive and earlier results were inspected before supplementary protocols were recorded; evidence for the first protocol freeze is partial. No untouched holdout or preregistration is claimed. Month-block intervals approximate temporal dependence, but do not adjust for the full specification search, arbitrary changes in the relationship, or all dependence across the period boundary. Separate multiplicity sensitivities do not establish familywise coverage across every analysis in this article. Online Resource 1, Section S13, maps each estimand to its evidence status.

Generative AI tools, including ChatGPT, assisted research organization, code-related work, and manuscript drafting and revision. Their use included generative drafting, not only copy editing. The authors remain responsible for the analysis, citations and final manuscript. Each completed numerical stage and its checks are versioned separately. This manuscript integrates those stages without treating later specification decisions as prospective registration.

## 5 Quantity and price findings

We first present the two core associations on their own outcome scales. The quantity result concerns standardized co-variation between reports; the German result concerns basis points of an official signed price comparison. A common explanatory field links these questions, but the estimands are neither interchangeable nor successive stages of a demonstrated mechanism. Historical and composition checks follow in Section 6 so that the principal findings and their immediate limitations can be assessed before the larger set of sensitivity results.

### 5.1 Pooled quantity association

The two transformations give nearly identical standardized associations (Table 4). Residual correlations are 0.6496 under A and 0.6486 under C, with three-month block intervals [0.5714, 0.7422] and [0.5660, 0.7402]. Corresponding slopes are 0.8802 and 0.8797. The comparison uses exactly the same auctions; no zero-standard-deviation observations distinguish the samples.

Table 4 Pooled conditional association

| Transformation | β | 95% interval for β | θ | 95% interval for θ |
| --- | --- | --- | --- | --- |
| A: log-one-plus | 0.8802 | [0.7506, 1.0384] | 0.6496 | [0.5714, 0.7422] |
| C: natural log | 0.8797 | [0.7627, 1.0143] | 0.6486 | [0.5660, 0.7402] |

Note: Each row uses 1,281 successful auctions, the full controls and reporting-series and year–month effects. Intervals use 999 three-month block draws. The planned positive-sample log-one-plus specification B equals A and is not duplicated. The intervals are exploratory, as described in Section 4.4.

The partial R2 is approximately 0.422 under A and 0.421 under C. These values describe the in-sample reduction in residual squared error relative to the fitted control-only model, not validation of one indicator as a substitute for the other. They do not describe a proportion of total market variation explained or an out-of-sample improvement. To illustrate the association on its transformed scale, the frozen estimates imply fitted contrasts of 0.0816 under A and 0.1408 under C across their respective observed interquartile ranges of residualized bid dispersion. Different transformations have different units, so equality of those contrasts is neither expected nor required.

The pooled correlation intervals remain positive in the one- and six-month block checks (Online Resource 1, Table S2). Both principal slope intervals in Table 4 include one. A slope across reports is not a within-auction comparison of an identical bidder population, however, so its value relative to one does not test dispersion compression.

### 5.2 Price association beyond the specified baseline

Adding bid dispersion to the fixed baseline gives κ = −78.72 basis points per unit of x (Table 5). The observed interquartile range of x is 0.1843, yielding a fitted signed-deviation difference of −14.51 basis points and a CR1-t interval of [−23.00, −6.01]. The restricted wild-cluster test gives p = 0.005; the mean-centred quarter-jackknife coefficient interval is [−136.54, −20.90]. These are differently constructed uncertainty summaries, not three independent confirmations. The incremental partial R-squared is 0.0681, describing residual variation in this sample rather than out-of-sample accuracy.

Table 5 Bid dispersion and official-reported price deviations in German auctions

| Specification | n / G | κ [95% CI] | IQR(x) | IQR contrast[95% CI], bp | Partial R² |
| --- | --- | --- | --- | --- | --- |
| Primary: signed | 240/21 | −78.72[−124.80, −32.64] | 0.1843 | −14.51[−23.00, −6.01] | 0.0681 |
| S1: absolute | 240/21 | 41.35[−13.58, 96.29] | 0.1843 | 7.62[−2.50, 17.74] | 0.0189 |
| S2: no row flags | 203/18 | −81.46[−138.39, −24.53] | 0.1856 | −15.12[−25.68, −4.55] | 0.0744 |
| S3: best bid only | 236/21 | −83.62[−129.71, −37.54] | 0.1828 | −15.29[−23.71, −6.86] | 0.0758 |

Note: One primary and three secondary specifications are retained. Within each row, the baseline and extension use identical observations. κ is in basis points per unit of log(1 + reported bid ratio); n/G gives auctions/quarters. Each interquartile-range (IQR) contrast uses the observed x range in that row. Intervals use quarter-cluster CR1 covariance and t(G−1), not bootstrap quantiles. The partial R² is an in-sample measure. The absolute outcome concerns magnitude, unlike the primary signed outcome. Section 4.2 defines the model and inference; Table 3 supplies the unconditional price context.

Figure 2 displays the interquartile contrasts and their CR1-t intervals. The negative signed association also appears in the 203-observation no-row-flag subset and the 236-observation best-bid subset, with contrasts of −15.12 and −15.29 basis points. Each subset uses its own observed dispersion range, so differences between these contrasts reflect both the coefficient and its scale. The residualized-x contrast for the primary sample is separately reported as −10.16 basis points in Online Resource 1, Table S12. It is not substituted for the prespecified observed-x display.

Fig. 2 Fitted price-deviation contrasts over an observed interquartile range of transformed bid dispersion; circles show signed-outcome models and the separated square shows the absolute-outcome model. Horizontal bars are exploratory quarter-cluster CR1-t 95% intervals, not wild-bootstrap intervals. Each row uses its own observed x range. Negative signed contrasts do not imply smaller absolute deviations. Values are the same as Table 5 and are not additional estimates

### 5.3 Absolute deviations, source restrictions and year influence

The absolute-outcome contrast is +7.62 basis points with interval [−2.50, 17.74]. This interval neither establishes smaller absolute deviations nor demonstrates that the association is exactly zero. It therefore limits the interpretation of the negative signed result: the evidence concerns the conditional location of the reported comparison, not greater proximity to a benchmark. Because the report scale has both signs, the signed mean can also reflect cancellation. Dividing the fitted contrast by that mean, or by the absolute median in Table 3, would not yield a return, an explained-share estimate or an efficiency measure.

Year deletion reveals an important limit to the magnitude. All six leave-one-year-out coefficients are negative, ranging from −88.23 to −45.12, but removing 2022 changes the coefficient from −78.72 to −45.12. This is substantial attenuation, not evidence that the association has a common strength across years. The diagnostic supplies no deletion-specific significance conclusion and does not allocate a share of the effect to 2022. Complete coefficients are in Online Resource 1, Table S13. They are retained rather than used to select a revised estimation period.

The source restrictions and numerical conditioning offer additional context without resolving these economic limits. The primary design is full rank, with a scaled condition number of 14.76. The largest quarter share of focal partial leverage is 0.0910; the concentration-equivalent count is 16.33 quarters. This is a design diagnostic, not an alternative count of independent observations. The no-row-flag sample has only 18 quarters, and the four last-trade references in the primary sample do not support a separate economic interpretation of that indicator. The best-bid result shows that those four observations are not essential to the negative point estimate, not that reference measurement is homogeneous.

## 6 Historical scope and sensitivity

The historical checks qualify the quantity finding along three dimensions: differences between periods, sensitivity to selected observable composition, and recurrence in an additional short time segment. They are not tests of the stability of the German price coefficient. We keep these questions distinct because persistence of a quantity association in 2026 cannot validate a price result estimated on a different subset during 2020–2025.

### 6.1 Period-specific quantity relationships

Conditional association is higher in the later historical sample (Table 6). Panel A reports correlations of 0.5501 and 0.7798 under A, and 0.5414 and 0.7719 under C, in 2020–2022 and 2023–2025 respectively. Panel B retains the originally designated slope contrasts; Panel C and Fig. 3 report the direct, secondary correlation contrasts. The two contrast scales are not interchangeable.

Table 6 Historical period comparison

Panel A: Period-specific estimates

| Spec. | Period | n | β | θ [95% interval] |
| --- | --- | --- | --- | --- |
| A | 2020–2022 | 643 | 0.6728 | 0.5501 [0.4570, 0.6486] |
| A | 2023–2025 | 638 | 1.1825 | 0.7798 [0.6757, 0.8892] |
| C | 2020–2022 | 643 | 0.6880 | 0.5414 [0.4394, 0.6493] |
| C | 2023–2025 | 638 | 1.1232 | 0.7719 [0.6645, 0.8829] |

Panel B: Late-minus-early slope differences

| Transformation | Δβ | 97.5% interval |
| --- | --- | --- |
| A | 0.5097 | [0.3340, 0.7222] |
| C | 0.4353 | [0.2605, 0.6344] |

Panel C: Late-minus-early residual-correlation differences (secondary exploratory contrasts)

| Transformation | Δθ | Exploratory 95% interval |
| --- | --- | --- |
| A | 0.2297 | [0.0875, 0.3681] |
| C | 0.2305 | [0.0808, 0.3748] |

Note: All nuisance coefficients are estimated separately in the two halves. The frozen 999 paired draws resample three-month blocks independently within each 36-month half, using common indices across transformations. Panel A gives 95% intervals for each period’s correlation. Panel B retains the primary slope contrasts and their 97.5% intervals. Panel C displays the already computed secondary correlation contrasts with 95% intervals, without multiplicity adjustment across transformations. This presentation does not promote Panel C to a prospectively primary analysis. Historical selection and cross-boundary dependence limitations apply to all panels.

The direct correlation differences are 0.2297 under A and 0.2305 under C, with secondary 95% intervals of [0.0875, 0.3681] and [0.0808, 0.3748]. The primary slope differences are 0.5097 and 0.4353, with the distinct 97.5% intervals shown in Panel B. Thus, both scales describe a stronger fitted relationship in the later sample under the stated exploratory scheme. The evidence for the correlation contrast is its own interval, not significance of Δβ or non-overlap of period-specific bars.

Fig. 3 Late-minus-early differences in residual correlation, comparing 2023–2025 with 2020–2022; squares mark the two transformations identified by their row labels. Bars reproduce the frozen secondary exploratory 95% intervals, without adjustment across transformations. The vertical line marks zero difference. Primary slope contrasts and their 97.5% intervals are reported separately in Table 6, Panel B

The marginal levels move differently: the median bid ratio is 1.520 in 2020–2022 and 1.255 in 2023–2025, while award medians are 1.443 and 1.356 (Online Resource 1, Table S5). Lower report-ratio levels thus coexist with stronger conditional association. This is a comparison of auctions, not matched bidders, and does not establish improved equality. The January 2023 boundary is a historical split, not an identified policy intervention.

### 6.2 Selected composition moments and residual distribution differences

The overlap-weighted differences remain positive: 0.1971 under A and 0.1937 under C (Table 7). Their exploratory 97.5% intervals are [0.0947, 0.3029] and [0.0847, 0.3051]. The paired changes from equal weighting are −0.0326 and −0.0368, with 95% intervals [−0.1349, 0.0802] and [−0.1449, 0.0797]. Because these paired intervals include zero, the analysis does not establish that weighting reduced the contrast, or quantify a fraction attributable to composition.

Table 7 Composition-weighted association and distributional diagnostics

Panel A: Weighted residual correlations and late-minus-early differences

| Spec. | Early θ | Late θ | Difference | 97.5% interval |
| --- | --- | --- | --- | --- |
| A | 0.5703 | 0.7675 | 0.1971 | [0.0947, 0.3029] |
| C | 0.5649 | 0.7586 | 0.1937 | [0.0847, 0.3051] |

Panel B: Empirical distribution distances before and after weighting

| Log variable | Original KS distance | Weighted KS distance |
| --- | --- | --- |
| Auction volume | 0.2810 | 0.2908 |
| Total bidders | 0.1080 | 0.0364 |
| Successful bidders | 0.0454 | 0.0201 |
| Cover ratio | 0.1142 | 0.0579 |

Note: Each weighted comparison retains 643 early and 638 late auctions. The period-membership and outcome models are refitted in 999 three-month block draws. Included-term mean differences are below 1.6×10⁻¹⁵; weight-concentration effective sample sizes are 586.55 and 614.75, not independent temporal sample sizes. KS denotes the Kolmogorov–Smirnov distance, the maximum difference between empirical cumulative distributions, not a p-value. Tables S7–S8 provide paired changes and block sensitivities.

Matching the selected moments does not match the full distributions. Log auction-volume KS distance increases from 0.2810 to 0.2908 even though its first and second moments balance; the other three distances decrease. The evidence supports a positive period contrast under this particular moment standardization, not invariance to all composition differences. The volume diagnostic was not used to select a different weight model or sample.

### 6.3 Additional 2026 quantity evidence

The January–September 2026 sample also shows positive association. Residual correlations are 0.8494 and 0.8350, with slopes 1.3137 and 1.2375. All leave-one-month-out correlations remain positive: 0.8396–0.8626 for A and 0.8230–0.8569 for C. These are same-market, new-period estimates from 166 auctions, not predictive accuracy or a formal test of further strengthening after 2025.

The original block intervals and complete enumeration results are retained in Online Resource 1, Table S9. Non-circular and circular sampling produce different diagnostic percentile ranges; neither expands the nine-month historical record. Accordingly, the additional sample supports the recurrence of the positive direction, with limited evidence about temporal uncertainty. It is not used as a confirmatory replication or as a substitute for the historical sample.

### 6.4 Conditioning sets and influence

The positive direction is not confined to the full conditioning set (Online Resource 1, Fig. S1). With series and year–month effects only, residual correlations are 0.6243 and 0.6197. Adding volume and total bidders gives 0.6289 and 0.6239. The relationship is therefore present without the cover ratio and successful-bidder count as controls. These are different descriptive projections, not an exogeneity or collider-bias test.

The completed deletion checks retain a positive association (Online Resource 1, Table S3). They remove observations, months, years or reporting series without replacing the principal sample. Omitting the 13 largest-Cook-distance observations gives correlations of 0.6911 and 0.6930; this is an influence diagnostic, not a revised data-cleaning rule. No observation is classified as erroneous solely because it is influential.

Within-series correlations are positive under both transformations (Online Resource 1, Table S4). EU, DE and PL are reporting series within one market, not independent replications. The PL comparison has 166 observations and only 90 residual degrees of freedom. These diagnostics address specified sources of sensitivity; they do not exclude shared determinants of bidding and awards.

## 7 Discussion

### 7.1 What information is added?

The two analyses identify different kinds of information in the same reporting system. Aggregate quantities and participation do not fully summarize the observed conditional co-variation of bid and award dispersion. In the German subset, the bid-side statistic is also associated with an official price comparison after conditioning on the stated conventional variables. This second finding is not implied by the first: strong bid–award co-variation could coexist with no incremental price association. Presenting both establishes the scope of the empirical information more clearly than interpreting the quantity correlation as a mechanism.

The result is economically interpretable at the level at which it is measured. The outcome is a recorded comparison between an auction clearing price and a secondary-market reference, and the fitted contrast has basis-point units. The contrast of −14.51 basis points is consequently more informative than an isolated coefficient in transformed units. Its uncertainty and the unconditional distribution should be read together, not collapsed into a claim of large benefits. Neither a statistical rejection nor an in-sample partial R-squared tells how much a participant would save, whether a reference is executable, or whether the same specification would predict future auctions.

Relative to the direct auction-price literature, the extension tests a particular additional report field, not the general proposition that participation or demand matters. Retaining submitted-price range in the baseline avoids treating quantity dispersion as if it were an untested substitute for price variation. Conversely, the coefficient does not establish superiority of one dispersion measure, nor does it show that all nonlinear or interaction effects of conventional variables have been absorbed. The increment is conditional on a transparent linear benchmark. Its value is an empirical relationship that subsequent studies can challenge on other samples or richer data, rather than a validated decision rule.

The two-sample design makes the scope of the evidence explicit. Broad quantity coverage allows the joint report statistics to be characterized across the EU, DE and PL series. The price comparison adds an economic outcome on a narrower, source-qualified German sample. Retaining these layers separately is preferable to silently presenting the price finding as a result for the full market. The resulting evidence is a conditional characterization of published fields, not validation of a latent competition index or a claim that the German subset represents all European auctions.

### 7.2 Economic interpretation and historical scope

The signed and absolute results also suggest a useful reporting discipline. When a relative price comparison can lie on either side of zero, a signed coefficient and a coefficient for its modulus answer different questions. Here only the signed model supplies a precise directional association under the specified approximations. It would therefore be misleading to summarize the extension as prices becoming closer to the reference. The estimate is equally insufficient to infer strategic bid shading: that interpretation would require both an authenticated economic sign convention and information capable of distinguishing bidding behaviour from other jointly determined conditions.

Historical heterogeneity provides a second reason to avoid a universal interpretation. In the quantity sample, lower marginal report ratios coexist with stronger conditional association; matching selected composition moments does not remove the full distributional difference in auction volume. In the price sample, omitting 2022 materially changes the coefficient. These findings limit two different claims: a stable correspondence between quantity indicators and a stable magnitude of the price association. Neither identifies a policy break, and the selected calendar boundary should not be assigned an institutional interpretation after the fact.

For analysis of public auction reports, the practical implication is methodological rather than a demonstrated trading recommendation. Levels, conditional co-variation and signed price location should be separated, with the source population and uncertainty method stated for each. The price result gives a concrete reason to assess the descriptive redundancy of quantity fields instead of assuming that participant counts and coverage exhaust their information. It does not establish that a monitoring system using this variable would make better decisions. That separate question lies beyond the evaluated outcomes.

### 7.3 Measurement, identification and inferential boundaries

Measurement and source selection define the first boundary. The means and standard deviations are retained as reported; their arithmetic ratios are not authenticated matched-population inequality measures. Reporting participants can represent clients, and the underlying variance divisors remain incompletely documented. The German analysis additionally conditions on source eligibility. Its best-bid and last-trade references are not independently reconstructed midpoints, and native quote age and an independently authenticated Coordinated Universal Time (UTC) event history are unavailable. These restrictions do not invalidate analysis of the reported numbers, but narrow the population and economic meaning of its coefficient.

Simultaneity defines the second boundary. Participation, demand coverage, awards and the clearing price arise in the same auction. The clearing-price control is also a component of the comparison being studied. It defines a conditional projection rather than the total effect of bid dispersion on auction pricing. Reduced-control quantity models and source-subset price models are sensitivity exercises, not remedies for endogenous selection or omitted demand conditions. Nor does conditioning on annual or monthly indicators ensure that every common market shock has been removed.

Inference defines the third boundary. The interval families do not adjust for the complete research history. Quarter clustering assumes a suitable across-quarter approximation, and a wild-cluster test cannot establish that assumption from 21 quarters. The shorter source subset has fewer clusters. The separate 2026 quantity exercise has only nine months; finite enumeration removes Monte Carlo variation for a specified resampling scheme, not uncertainty about its repeated-sample coverage. The surviving directions are therefore reported with their estimand-specific limitations rather than combined into a single confirmatory claim.

Finally, the official percentage convention is preserved. The targeted methods-text review of 24 reports did not establish an explicit subtraction-and-denominator equation, and the study does not infer one from rounded values. We describe the result as a lower official-reported signed deviation rather than a wider discount. This prevents a stronger economic direction from being attributed to the data than the source review supports. Exact raw-data reproduction also depends on lawful access to the author-held matched rows and the archived 2026 quantity snapshot, as detailed below and in Online Resource 1.

## 8 Conclusion

Reported quantity dispersion contains two distinct conditional relationships in this archive. Across 1,281 successful EUA auctions in 2020–2025, bid and award ratios have residual correlations near 0.65. In the matched sample of 240 German auctions, bid dispersion is associated with a lower official-reported signed price deviation beyond the specified conventional auction controls and the same-auction price level. Its fitted observed-interquartile contrast is −14.51 basis points, with an exploratory quarter-clustered interval of [−23.00, −6.01].

The associated limits are substantive findings, not ancillary qualifications. The absolute-price-deviation interval includes zero, the signed coefficient is sensitive in magnitude to 2022, and quantity-period comparisons remain subject to incomplete composition balance. The short 2026 quantity record adds temporal scope without validating a forecasting rule. Together, these results distinguish quantity co-variation from the signed location and absolute magnitude of reported price comparisons. They contribute a reproducible specification and bounded empirical evidence, while leaving causal allocation, bidder-level inequality, pricing efficiency and operational returns unestablished.

## Data and computer code availability

The public code, aggregate outputs and versioned documentation are available at https://github.com/124-creator/-123. The historical quantity input is identified by commit 5745eb3ddca79602346053446583d794b0e09800; the price analysis by fccd471de96548bd781c59aced4a59435aae08ac; and the price descriptions and source-definition record by 33707c164c80accd7acf9fcd3f0965088a8370f6. Online Resource 1, Section S18, gives direct links and distinguishes reproduction of published arithmetic from refitting the event-level models. Online Resource 2 provides a machine-readable catalogue of the 24 official report sources, page locators and fixed file identities.

The matched German event-level tables and underlying official PDFs are held by the authors but are not included in the public package because bulk redistribution rights have not been established. Requests concerning these files, source reconstruction or exact-snapshot verification should be directed to Zhongfei Tian at 15517837680@163.com. Any transfer of third-party material is conditional on the relevant provider's permission; the public source catalogue and analysis instructions are the first access route. The exact 2026 quantity snapshot is also absent from the public package. Its recorded hash identifies the required bytes but does not guarantee that the changing provider URL still supplies them. Public outputs alone therefore do not permit a complete independent event-level refit.

## Statements and Declarations

Funding: The authors received no financial support for this research.

Competing interests: The authors declare that they have no financial interests relevant to this article.

Author contributions: Zhongfei Tian coordinated the study and manuscript preparation and completed the final revisions. Xiang Wang reviewed and checked the manuscript, approved its scientific content, and authorized Zhongfei Tian to complete the final editorial revision.

## Supplementary information

Online Resource 1 Field definitions, supplementary estimates, dependence diagnostics, study sequence and data-access instructions

Online Resource 2 Machine-readable catalogue of the 24 official German quarterly reports, page locators and source-file identities

## References

Ausubel LM, Cramton P, Pycia M, Rostek M, Weretka M (2014) Demand reduction and inefficiency in multi-unit auctions. The Review of Economic Studies 81:1366–1400. https://doi.org/10.1093/restud/rdu023

Bosco B (2023) Trade, equilibrium prices and rents in European auctions for emission allowances. Environmental Economics and Policy Studies 25:87–113. https://doi.org/10.1007/s10018-022-00344-y

Cook RD (1977) Detection of influential observation in linear regression. Technometrics 19:15–18. https://doi.org/10.1080/00401706.1977.10489493

Cramton P, Kerr S (2002) Tradeable carbon permit auctions: how and why to auction not grandfather. Energy Policy 30:333–345. https://doi.org/10.1016/S0301-4215(01)00100-8

EEX (n.d.) Frequently Asked Questions: Emissions Auctions. European Energy Exchange. https://www.eex.com/en/faq. Accessed 10 October 2026

European Commission (2024) Auctions by the Common Auction Platform: April, May, June 2024. https://climate.ec.europa.eu/document/download/d962459c-021e-4901-b49f-e5d37e5d2c93_en?filename=cap_report_202406_en.pdf. Access record: 10 October 2026

European Securities and Markets Authority (ESMA) (2025) Market Report on EU carbon markets. ESMA50-481369926-30552. https://www.esma.europa.eu/sites/default/files/2025-10/ESMA50-481369926-30552_Carbon_Markets_Report_2025.pdf. Accessed 10 October 2026

German Emissions Trading Authority (DEHSt) (2020–2025) Quarterly reports on German auctions of emission allowances. Umweltbundesamt, Berlin. Report-specific editions, Table 4 page locators and source URLs are recorded in Online Resource 1, Section S17, and the accompanying source ledger.

Hackl F, Hölzl-Leitner M, Pennerstorfer D (2026) Measuring product differentiation by observing consumer search. Empirical Economics 70:78. https://doi.org/10.1007/s00181-026-02925-2

Kronmal RA (1993) Spurious correlation and the fallacy of the ratio standard revisited. Journal of the Royal Statistical Society: Series A 156:379–392. https://doi.org/10.2307/2983064

Lahiri SN (2003) Resampling methods for dependent data. Springer, New York. https://doi.org/10.1007/978-1-4757-3803-2

Li F, Morgan KL, Zaslavsky AM (2018) Balancing covariates via propensity score weighting. Journal of the American Statistical Association 113:390–400. https://doi.org/10.1080/01621459.2016.1260466

Lovell MC (1963) Seasonal adjustment of economic time series and multiple regression analysis. Journal of the American Statistical Association 58:993–1010. https://doi.org/10.1080/01621459.1963.10480682

MacKinnon JG, Nielsen MØ, Webb MD (2023) Fast and reliable jackknife and bootstrap methods for cluster-robust inference. Journal of Applied Econometrics 38:671–694. https://doi.org/10.1002/jae.2969

Meijer E, Postepska A, Wansbeek T (2025) Handling multiple proxies. Empirical Economics 69:2901–2926. https://doi.org/10.1007/s00181-025-02825-x

Niu H, Liu T (2024) Forecasting the volatility of European Union allowance futures with macroeconomic variables using the GJR-GARCH-MIDAS model. Empirical Economics 67:75–96. https://doi.org/10.1007/s00181-023-02551-2

Otsubo Y (2026) Intraday and daily price discovery in carbon markets: EUA futures versus carbon ETFs. International Review of Finance 26:e70099. https://doi.org/10.1111/irfi.70099