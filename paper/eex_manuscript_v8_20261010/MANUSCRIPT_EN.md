# Bid and award dispersion in European carbon auctions

Conditional association and composition sensitivity

**Zhongfei Tian · Xiang Wang**

Zhengzhou University of Aeronautics, Zhengzhou, Henan, China

**Corresponding author:** Zhongfei Tian · 15517837680@163.com

## Abstract

Quantity statistics in carbon-auction reports describe both the scale of bidding and the dispersion of quantities bid and won. We examine the joint information in two reported dispersion ratios using 1,281 successful European Union Allowance auctions during 2020--2025. Each ratio is a reported standard deviation divided by its reported mean; their underlying bidder populations are not assumed to match. After controlling for auction volume, bidder counts, demand coverage, reporting series and year--month effects, residual correlations are 0.650 and 0.649 under two transformations. Correlations are about 0.55 in 2020--2022 and 0.78 in 2023--2025, despite lower marginal medians of both ratios in the later period. Descriptive overlap weighting balances selected composition means and second moments, with weighted correlation differences of 0.197 and 0.194. Auction-volume distributions nevertheless remain unequal, limiting the comparison to the selected moments. A separate January--September 2026 sample of 166 auctions also exhibits positive association; its nine-month record supports only limited temporal diagnostics. The findings show that dispersion levels, conditional co-variation and historical scope are distinct features of these published statistics. They provide a measurement-explicit empirical description rather than evidence of allocation effects or forecasting value. All uncertainty assessments remain exploratory and do not adjust for the historical specification search.

**Keywords:** European Union Allowances; primary auctions; quantity dispersion; participation; measurement; temporal heterogeneity

**JEL classification:** D44; C13; Q58

## 1 Introduction

Carbon-auction reports contain information about how much is bid, how many participants bid, and how quantities are dispersed. These dimensions describe different aspects of a primary allowance market. The European Commission publishes quantity moments alongside auction volume and bidder counts, while the European Securities and Markets Authority (ESMA) monitors participation and concentration (European Commission 2024; ESMA 2025). Marginal summaries locate each indicator separately. A joint analysis asks whether reports with unusually dispersed bidding also have unusually dispersed awards after accounting for scale and participation, and whether the same relationship characterizes different periods.

Awards originate in bids, so a positive relationship is plausible. Its magnitude is not fixed by auction totals and participant counts, however, and a lower level of dispersion need not imply a weaker relationship between bid-side and award-side measures. We ask two descriptive questions: how strong is their conditional association, and how much does it differ between the historical periods 2020--2022 and 2023--2025? Because the reported moments can refer to different groups, the object is a relationship between auction reports, not a before-and-after comparison of the same bidders.

The main sample comprises 1,281 successful European Union Allowance (EUA) auctions in the EU, DE and PL reporting series of the European Energy Exchange (EEX). We relate the two reported standard-deviation-to-mean ratios using common samples, two transformations, and controls for scale, participation, reporting series and year--month. The historical comparison estimates all nuisance coefficients separately in each period. A supplementary overlap-weighted analysis examines sensitivity to selected observed composition moments; a separate 2026 sample examines whether the positive direction also appears outside the original years.

The main finding combines levels and co-variation. Residual correlations are about 0.65 in the pooled sample and are higher in the later historical period, even though both report ratios have lower marginal medians. Weighted period differences remain about 0.20 after balancing selected composition moments. This does not establish full comparability: the auction-volume distributions remain unequal. The 2026 sample also has a positive relationship, but its nine-month span provides limited information about temporal uncertainty.

The contribution is an auction-level characterization of shared quantity variation and its historical scope. Relative to price-focused auction analysis such as Bosco (2023), the outcome is reported quantity dispersion rather than price volatility. Relative to official marginal reporting, the analysis quantifies a conditional joint relationship and separates changes in indicator levels from changes in their association. The weighting and time-extension exercises qualify that description rather than identify a mechanism. We do not claim a new estimator, prior misuse of official statistics, or a demonstrated pricing or monitoring benefit.

The historical data and earlier findings were examined before supplementary checks were specified. The study is therefore retrospective and exploratory. Section 2 introduces the market and measurement context; Section 3 defines the estimands and inferential limits; Section 4 presents the results. Sections 5 and 6 discuss their economic interpretation and scope. Online Resource 1 provides the field definitions, detailed diagnostics, study sequence and reproduction record.

## 2 Auction context and related research

### 2.1 Allocation, participation and quantities

EEX describes its emissions auctions as single-round, sealed-bid, uniform-price auctions. Bids are ranked by price, successful orders pay the clearing price, and marginal execution can be partial. Participants may bid on their own account or on behalf of clients (EEX n.d.). A reporting participant therefore need not be the final installation using allowances for compliance. This distinction matters for the quantities and counts studied here, which cannot be converted into client-level demand without additional information.

Allowance auction design matters for rents and allocation as well as the clearing price (Cramton and Kerr 2002). Multi-unit auction theory links bidding incentives and demand reduction to allocation outcomes (Ausubel et al. 2014). These considerations motivate attention to quantity distributions. Our data contain public aggregate moments rather than valuations or participant-specific bid schedules, so they support a description of quantity co-variation, not a test of strategic demand reduction.

The available observations distinguish auction-level totals, reported distributional summaries and bidder-level mechanisms. The first two are observed; the third is not recovered by aggregate regressions.

### 2.2 Direct comparisons and measurement interpretation

Bosco (2023) studies Phase III EUA primary-auction prices and return volatility using a bidding model and GARCH specifications, with participation and the cover ratio among the explanatory variables. Its bid spread is a price variable, not a quantity standard deviation. Niu and Liu (2024) forecast EUA futures volatility with macroeconomic information. Our analysis instead concerns two quantity summaries in the same completed auction. Neither a temporal price forecast nor a price-premium equation is estimated.

Official reporting provides the closest measurement context. The Commission distinguishes individual-auction means from monthly aggregates and describes bid and award means using participating and successful bidders, respectively (European Commission 2024). ESMA (2025) treats participation and concentration as distinct indicators with different data sources. Quantity dispersion is thus an established reporting dimension. We add a conditional comparison of the two report measures and its historical scope, rather than introduce the fields themselves.

Two measurement cautions shape the design. Shared ratio components can affect regression relationships, so normalizing by a mean is not a substitute for making totals and counts explicit (Kronmal 1993). In addition, association between observed indicators does not identify a latent common factor. The multiple-proxy framework of Meijer et al. (2025) makes the identification and normalization conditions for that different task explicit. We impose no such factor model. The analysis retains the original report fields, examines the specified transformations and control sets, and uses a separate algebraic check to explain the role of constructed denominators.

## 3 Data and empirical design

### 3.1 Reporting archive and sample definition

The data are six EEX annual primary-auction workbooks for 2020--2025, preserved in a fixed research snapshot. Extracting every dated row yields 1,327 records. The sample retains product code T3PA, the EU/DE/PL reporting series and an explicit successful status. The rule excludes 38 other-product records, five records outside the specified series and three cancelled auctions. It leaves 1,281 unique auctions between 7 January 2020 and 15 December 2025, covering all 72 calendar months. Table 1 gives their distribution. The three series belong to the same allowance market and are not independent-market replications.

**Table 1 Sample composition by year and reporting series**

  -----------------------------------------------------------------------
  **Year**            **EU**       **DE**       **PL**       **Total**
  ------------------- ------------ ------------ ------------ ------------
  2020                139          46           24           209

  2021                132          45           46           223

  2022                142          46           23           211

  2023                143          47           24           214

  2024                142          46           24           212

  2025                142          45           25           212

  Total               840          275          166          1281
  -----------------------------------------------------------------------

*Note:* Counts refer to successful T3PA auctions satisfying the stated series restriction. Cancelled auctions and other products are not recoded as zero outcomes. The first three years contain 643 auctions and the final three contain 638.

The selected sample has complete numeric fields for the fixed measures and controls. Both reported means are positive; neither standard-deviation field contains a zero. No auction is removed because its dispersion ratio is large or small. There is one selected auction per distinct date, but observations can remain dependent over time. Selection on successful completion defines the population of interest; the analysis does not describe cancelled auctions or latent demand.

Each record retains its source workbook, sheet and row. The completed source audit reconciled the exclusions and compared the numeric extraction with a separate XML-reading route. The audit establishes traceability of the supplied snapshot, not the first historical release of every field. Online Resource 1, Section S2, records the cell counts and verification scope.

For descriptive context, Table 2 reports the two dispersion ratios (reported standard deviation divided by reported mean), the conditioning variables and total bid volume. All summaries give each auction equal weight. Volumes are displayed in millions of tCO2; ratios and counts retain their original scales. Quartiles use linear interpolation. No winsorization, trimming or additional sample restriction is applied.

**Table 2 Descriptive statistics of the successful-auction sample**

  ----------------------------------------------------------------------------------------
  **Variable**             **Mean**   **Q1**   **Median**   **Q3**   **Min.**   **Max.**
  ------------------------ ---------- -------- ------------ -------- ---------- ----------
  Bid ratio $r^{b}$        1.404      1.202    1.387        1.579    0.847      2.622

  Award ratio $r^{w}$      1.422      1.215    1.399        1.598    0.443      2.707

  Cover ratio $R$          1.825      1.540    1.740        2.030    1.010      3.780

  Auction volume $V$       2.675      2.296    2.651        3.245    0.970      6.399

  Submitted volume $B$     4.717      3.986    4.736        5.321    1.937      12.899

  Total bidders $N$        22.663     20       23           25       12         31

  Successful bidders $S$   16.878     14       17           20       3          27
  ----------------------------------------------------------------------------------------

*Note:* All rows use 1,281 auctions. $V$ and $B$ are in million tCO2, $N$ and $S$ are bidder counts, and the three ratios are dimensionless. $B$ maps to the source field "Total Amount of Bids" in the workbook's volume section, not to auction revenue. Q1 and Q3 are the 25th and 75th percentiles. These are marginal descriptive statistics, not conditional estimates or bidder-level distributional comparisons.

The separate sample medians are 23 participating bidders, 17 successful bidders, 2.651 million tCO2 of auction volume and a cover ratio of 1.740; these need not occur in one observed auction. Median bid and award ratios are 1.387 and 1.399. Figure 1 shows the period-specific medians and interquartile ranges, with full summaries in Online Resource 1, Table S5. These marginal quantities are distinct from the conditional correlations below.

![Auction-level medians and interquartile ranges of bid and award reported dispersion ratios in two historical periods. Bars are quartile ranges, not confidence intervals.](figures/Fig1.png){width="6.4in" height="2.8496347331583554in"}

**Fig. 1** Marginal reported dispersion ratios by historical period; diamonds denote auction-level medians and horizontal segments extend from the 25th to the 75th percentile. Each early-period row contains 643 auctions and each late-period row 638. These segments describe the middle half of the observations; they are not confidence intervals or paired-bidder comparisons. The figure reuses the descriptive statistics in Online Resource 1, Table S5

### 3.2 Reported measures and linear projection

Let $\mu_{t}^{b},s_{t}^{b}$ denote the reported mean and standard deviation of bid volume, and $\mu_{t}^{w},s_{t}^{w}$ the corresponding reported moments of volume won. Define

$r_{t}^{b} = \frac{s_{t}^{b}}{\mu_{t}^{b}},\quad\quad r_{t}^{w} = \frac{s_{t}^{w}}{\mu_{t}^{w}}.$ (1)

We call these *reported dispersion ratios*. The original labels refer to volume per bidder. Nevertheless, the population underlying each standard deviation and its variance divisor have not been conclusively matched to the paired mean throughout the archive. The ratios are therefore not interpreted as verified coefficients of variation for an identical population before and after allocation. This restriction affects the economic interpretation, not the arithmetic definition in (1).

Specification A sets $x_{t} = \log\left( 1 + r_{t}^{b} \right)$ and $y_{t} = \log\left( 1 + r_{t}^{w} \right)$. The main conditional projection is

$y_{t} = \beta x_{t} + \mathbf{\gamma}^{\prime}\mathbf{z}_{t} + \alpha_{j(t)} + \delta_{m(t)} + u_{t},$ (2)

where $j(t)$ denotes the reporting series, $m(t)$ the original year--month, and $\mathbf{z}_{t} = \left( \log R_{t},\log V_{t},\log N_{t},\log S_{t} \right)^{\prime}$. Here $R$ is the reported cover ratio, $V$ reported auction volume, $N$ total bidders and $S$ successful bidders. The submitted-volume field $B$, used in the denominator audit and Table 2, is labelled "Total Amount of Bids" in the source workbook; it is not an additional regressor in (2). All observations have equal weight. The pooled full design has rank 79 and 1,202 residual degrees of freedom.

The fixed supplementary measurement comparison contains A, a positive-standard-deviation version of A labelled B, and a natural-log version C on the same positive sample. Since all selected standard deviations are positive, A and B are identical. B is retained in the reproduction record as a sample-eligibility check rather than a separate result. C uses $x_{t} = \log r_{t}^{b}$ and $y_{t} = \log r_{t}^{w}$ on exactly the same 1,281 rows. No constant is added to a zero standard deviation.

All variables concern the same completed auction. In particular, the cover ratio and successful-bidder count are simultaneous outcomes, not instruments or inputs known before bidding. Equation (2) is an equal-auction-weighted descriptive linear projection for the selected archive. Its coefficient depends on the conditioning set and on the distribution of those auctions. To examine dependence on those conditions, we also report fixed effects alone and fixed effects plus $\log V$ and $\log N$. These models answer related, but not identical, conditional questions. Year--month effects account for monthly levels; they do not absorb every daily common shock.

Reported means are numerically consistent with total submitted volume divided by $N$ and reported auction volume divided by $S$, to the archive's displayed precision. This creates an explicit denominator structure. Under natural logs, constructed means and a constructed cover ratio yield additive identities that disappear after projection on the corresponding totals and counts. The log-one-plus transformation does not have that property. Online Resource 1 derives and checks these identities, keeping constructed fields separate from the reported fields used in (2).

### 3.3 Magnitude, dependence and sensitivity

Let $\mathbf{Z}$ contain the nuisance regressors and fixed effects in (2), and let $M_{Z}$ denote the residual-maker for that space. With $\widetilde{\mathbf{x}} = M_{Z}\mathbf{x}$ and $\widetilde{\mathbf{y}} = M_{Z}\mathbf{y}$, the coefficient and standardized association are

$\widehat{\beta} = \frac{{\widetilde{\mathbf{x}}}^{\prime}\widetilde{\mathbf{y}}}{{\widetilde{\mathbf{x}}}^{\prime}\widetilde{\mathbf{x}}},\quad\quad\widehat{\theta} = \widehat{\beta}\frac{s\left( \widetilde{\mathbf{x}} \right)}{s\left( \widetilde{\mathbf{y}} \right)}.$ (3)

This is the partial-regression representation (Lovell 1963). In the present equal-weight, single-added-regressor setting, $\widehat{\theta}$ is the sample correlation of the two residuals. The partial coefficient of determination satisfies

$R_{\text{partial}}^{2} = \frac{{SSE}_{Z} - {SSE}_{Z,x}}{{SSE}_{Z}} = {\widehat{\theta}}^{\, 2}.$ (4)

These are complementary scales for the same association, not independent pieces of evidence. The residual correlation is symmetric in the two indicators; placing award dispersion on the left of the regression does not establish a direction of transmission. Pooled and subperiod correlations use their respective fitted control spaces and variances, so a change in correlation need not be a change in a structural parameter. We also report the fitted transformed-response contrast corresponding to an observed interquartile range of residualized $x$. It is a scale illustration along the fitted partial regression, not an intervention or an expected procurement gain.

The principal uncertainty calculation uses a month-block resampling design for dependent observations, within the general class discussed by Lahiri (2003). It resamples non-circular blocks of three consecutive calendar months. Starting months are drawn with replacement; blocks are concatenated and truncated to a 72-month axis. All auctions in a selected month are retained jointly. Repeated months increase row multiplicities and retain their original fixed-effect labels. The entire conditional projection is re-estimated for each of 999 draws. A and C share the draw indices. One- and six-month blocks, with 199 draws each, provide bounded sensitivity checks. Intervals are percentile intervals with linear quantile interpolation.

We examine influence by deleting each observation, month, year and series, and by jointly omitting the 13 largest-Cook-distance observations under each specification (Cook 1977). These diagnostics do not redefine the main sample. Within-series models retain their own monthly effects; empty months retain their positions on the 72-month resampling axis. Reduced-control and within-series intervals use 499 and 399 three-month block draws, respectively.

### 3.4 Historical comparison and research process

The historical comparison divides 2020--2022 from 2023--2025, a split already present in earlier exploration. The two samples contain 643 and 638 observations, and all nuisance coefficients are estimated separately. Each 36-month half is independently resampled in three-month blocks for 999 paired draws, with common indices across transformations. The protocol's primary contrasts are late-minus-early slopes, *Δβ = β*~late~* − β*~early~. Each transformation receives a 97.5% percentile interval as a Bonferroni-style nominal family-95% sensitivity calculation, conditional on adequate individual interval approximations. We also display the previously computed secondary contrasts *Δθ = θ*~late~* − θ*~early~ with their exploratory 95% intervals. These are direct comparisons of standardized association; a slope-difference interval does not test a correlation difference. The secondary intervals are neither family-adjusted over the two transformations nor replacements for the originally designated primary contrasts.

The historical archive and earlier results were inspected before supplementary protocols were recorded; evidence for the first protocol freeze is partial. No untouched holdout or preregistration is claimed. Month-block intervals approximate temporal dependence, but do not adjust for the full specification search, arbitrary changes in the relationship, or all dependence across the period boundary. Separate multiplicity sensitivities do not establish familywise coverage across every analysis in this article. Online Resource 1, Section S13, maps each estimand to its evidence status.

Generative AI tools, including ChatGPT, assisted research organization, code-related work, and manuscript drafting and revision. Their use included generative drafting, not only copy editing. The numerical specifications, source checks and validation records are documented separately. The authors remain responsible for the analysis, citations and final manuscript. This editorial revision reports existing estimates without new model fitting or resampling.

### 3.5 Composition sensitivity of the historical comparison

We use descriptive overlap weights to emphasize auction characteristics represented in both historical periods. Following Li et al. (2018), one unpenalized logistic model predicts late-period membership from an intercept, the four pooled-standardized log controls, their squared terms, reporting-series indicators and month-of-year indicators. Neither dispersion measure, price, year nor specific year--month enters this model. Early weights are the fitted late-period probabilities; late weights are one minus those probabilities. Coverage and successful participation remain joint auction outcomes. The weights standardize selected observed moments and are not a causal treatment design.

Within each period, both transformed indicators are projected on the original controls and year--month effects by weighted least squares. We compute their weighted residual covariance and divide by the product of the weighted residual standard deviations, using the same weights throughout. The supplemental contrast is the late-minus-early difference in that correlation. Every block draw refits the period-membership model and both outcome projections. The main calculation uses 999 three-month draws, with 199 draws each for one- and six-month sensitivity checks. Individual 97.5% percentile intervals address the two weighted contrasts only as a limited multiplicity sensitivity. Weight concentration, fitted-term balance, distribution distances and the paired change from equal weighting are reported together. No outcome-dependent trimming or alternative weight-model search is used.

### 3.6 New-time sample and finite short-axis diagnostics

The additional sample uses the same product, success-status and series rules, with January--September 2026 fixed before its estimation. The annual file contains 173 dated rows; seven October rows are excluded, leaving 166 auctions: 111 EU, 35 DE and 20 PL. All nine months are represented, and required labels match the historical schema. Both specifications are re-estimated using 2026 year--month effects. The exercise therefore checks a relationship in a new time period of the same market, not predictions from a frozen historical model.

A nine-month axis provides only seven non-circular three-month source blocks. Following the initial 999 draws, a post-result diagnostic enumerates the finite non-circular and circular resampling distributions and deletes each month in turn. Non-circular sampling underweights endpoint months; circular sampling balances their expected inclusion but joins September to January artificially. The resulting ranges are short-axis diagnostics, not certified coverage intervals. Original results remain available in Online Resource 1, Section S11, and no formal difference between 2026 and earlier years is tested.

## 4 Results

### 4.1 Magnitude of the pooled relationship

The two transformations give nearly identical standardized associations (Table 3). Residual correlations are 0.6496 under A and 0.6486 under C, with three-month block intervals \[0.5714, 0.7422\] and \[0.5660, 0.7402\]. Corresponding slopes are 0.8802 and 0.8797. The comparison uses exactly the same auctions; no zero-standard-deviation observations distinguish the samples.

**Table 3 Pooled conditional association**

  ----------------------------------------------------------------------------------------------------------------------------
  **Transformation**   $\widehat{\beta}$   **95% interval for** $\beta$   $\widehat{\theta}$   **95% interval for** $\theta$
  -------------------- ------------------- ------------------------------ -------------------- -------------------------------
  A: log-one-plus      0.8802              \[0.7506, 1.0384\]             0.6496               \[0.5714, 0.7422\]

  C: natural log       0.8797              \[0.7627, 1.0143\]             0.6486               \[0.5660, 0.7402\]
  ----------------------------------------------------------------------------------------------------------------------------

*Note:* Each row uses 1,281 successful auctions, the full controls and reporting-series and year--month effects. Intervals use 999 three-month block draws. The planned positive-sample log-one-plus specification B equals A and is not duplicated. The intervals are exploratory, as described in Section 3.4.

The partial $R^{2}$ is approximately 0.422 under A and 0.421 under C. These values describe the in-sample reduction in residual squared error relative to the fitted control-only model, not validation of one indicator as a substitute for the other. They do not describe a proportion of total market variation explained or an out-of-sample improvement. To illustrate the association on its transformed scale, the frozen estimates imply fitted contrasts of 0.0816 under A and 0.1408 under C across their respective observed interquartile ranges of residualized bid dispersion. Different transformations have different units, so equality of those contrasts is neither expected nor required.

The pooled correlation intervals remain positive in the one- and six-month block checks (Online Resource 1, Table S2). Both principal slope intervals in Table 3 include one. A slope across reports is not a within-auction comparison of an identical bidder population, however, so its value relative to one does not test dispersion compression.

### 4.2 Controls, influence and reporting series

The positive direction is not confined to the full conditioning set (Fig. 2). With series and year--month effects only, residual correlations are 0.6243 and 0.6197. Adding volume and total bidders gives 0.6289 and 0.6239. The relationship is therefore present without the cover ratio and successful-bidder count as controls. These are different descriptive projections, not an exogeneity or collider-bias test.

![Residual correlations for log-one-plus and natural-log ratios across three conditioning sets, with exploratory 95 percent month-block intervals.](figures/Fig2.png){width="6.4in" height="3.4102187226596676in"}

**Fig. 2** Residual correlations across conditioning sets; A and C denote log-one-plus and natural-log ratios, respectively. Bars are exploratory 95% three-month block intervals, using 499 draws for the reduced controls and 999 for full controls. FE denotes reporting-series and year--month effects; full controls also include the cover ratio and successful-bidder count. Exact values are retained in Online Resource 1, Table S6. These rows are related descriptive projections, not independent replications

The completed deletion checks retain a positive association (Online Resource 1, Table S3). They remove observations, months, years or reporting series without replacing the principal sample. Omitting the 13 largest-Cook-distance observations gives correlations of 0.6911 and 0.6930; this is an influence diagnostic, not a revised data-cleaning rule. No observation is classified as erroneous solely because it is influential.

Within-series correlations are positive under both transformations (Online Resource 1, Table S4). EU, DE and PL are reporting series within one market, not independent replications. The PL comparison has 166 observations and only 90 residual degrees of freedom. These diagnostics address specified sources of sensitivity; they do not exclude shared determinants of bidding and awards.

### 4.3 Directional persistence and temporal heterogeneity

Conditional association is higher in the later historical sample (Table 4). Panel A reports correlations of 0.5501 and 0.7798 under A, and 0.5414 and 0.7719 under C, in 2020--2022 and 2023--2025 respectively. Panel B retains the originally designated slope contrasts; Panel C and Fig. 3 report the direct, secondary correlation contrasts. The two contrast scales are not interchangeable.

**Table 4 Historical period comparison**

*Panel A: Period-specific estimates*

  ---------------------------------------------------------------------------------------------
  **Spec.**   **Period**   $n$    $\widehat{\beta}$   $\widehat{\theta}$ **\[95% interval\]**
  ----------- ------------ ------ ------------------- -----------------------------------------
  A           2020--2022   643    0.6728              0.5501 \[0.4570, 0.6486\]

  A           2023--2025   638    1.1825              0.7798 \[0.6757, 0.8892\]

  C           2020--2022   643    0.6880              0.5414 \[0.4394, 0.6493\]

  C           2023--2025   638    1.1232              0.7719 \[0.6645, 0.8829\]
  ---------------------------------------------------------------------------------------------

*Panel B: Late-minus-early slope differences*

  ----------------------------------------------------------------------------------
  **Transformation**   $\Delta\widehat{\beta}$   **97.5% interval**
  -------------------- ------------------------- -----------------------------------
  A                    0.5097                    \[0.3340, 0.7222\]

  C                    0.4353                    \[0.2605, 0.6344\]
  ----------------------------------------------------------------------------------

*Panel C: Late-minus-early residual-correlation differences (secondary exploratory contrasts)*

  -----------------------------------------------------------------------------------
  **Transformation**   $\Delta\widehat{\theta}$   **Exploratory 95% interval**
  -------------------- -------------------------- -----------------------------------
  A                    0.2297                     \[0.0875, 0.3681\]

  C                    0.2305                     \[0.0808, 0.3748\]
  -----------------------------------------------------------------------------------

*Note:* All nuisance coefficients are estimated separately in the two halves. The frozen 999 paired draws resample three-month blocks independently within each 36-month half, using common indices across transformations. Panel A gives 95% intervals for each period's correlation. Panel B retains the primary slope contrasts and their 97.5% intervals. Panel C displays the already computed secondary correlation contrasts with 95% intervals, without multiplicity adjustment across transformations. This presentation does not promote Panel C to a prospectively primary analysis. Historical selection and cross-boundary dependence limitations apply to all panels.

The direct correlation differences are 0.2297 under A and 0.2305 under C, with secondary 95% intervals of \[0.0875, 0.3681\] and \[0.0808, 0.3748\]. The primary slope differences are 0.5097 and 0.4353, with the distinct 97.5% intervals shown in Panel B. Thus, both scales describe a stronger fitted relationship in the later sample under the stated exploratory scheme. The evidence for the correlation contrast is its own interval, not significance of $\Delta\beta$ or non-overlap of period-specific bars.

![Late-minus-early differences in residual correlation for two transformations, with secondary unadjusted exploratory 95 percent intervals.](figures/Fig3.png){width="6.4in" height="2.4759120734908135in"}

**Fig. 3** Late-minus-early differences in residual correlation, comparing 2023--2025 with 2020--2022; squares mark the two transformations identified by their row labels. Bars reproduce the frozen secondary exploratory 95% intervals, without adjustment across transformations. The vertical line marks zero difference. Primary slope contrasts and their 97.5% intervals are reported separately in Table 4, Panel B

The marginal levels move differently: the median bid ratio is 1.520 in 2020--2022 and 1.255 in 2023--2025, while award medians are 1.443 and 1.356 (Online Resource 1, Table S5). Lower report-ratio levels thus coexist with stronger conditional association. This is a comparison of auctions, not matched bidders, and does not establish improved equality. The January 2023 boundary is a historical split, not an identified policy intervention.

### 4.4 Composition weighting: persistence with incomplete distributional balance

The overlap-weighted differences remain positive: 0.1971 under A and 0.1937 under C (Table 5). Their exploratory 97.5% intervals are \[0.0947, 0.3029\] and \[0.0847, 0.3051\]. The paired changes from equal weighting are −0.0326 and −0.0368, with 95% intervals \[−0.1349, 0.0802\] and \[−0.1449, 0.0797\]. Because these paired intervals include zero, the analysis does not establish that weighting reduced the contrast, or quantify a fraction attributable to composition.

**Table 5 Composition-weighted association and distributional diagnostics**

Panel A: Weighted residual correlations and late-minus-early differences

  ---------------------------------------------------------------------------------------
  **Spec.**   **Early θ**   **Late θ**   **Difference**   **97.5% interval**
  ----------- ------------- ------------ ---------------- -------------------------------
  A           0.5703        0.7675       0.1971           \[0.0947, 0.3029\]

  C           0.5649        0.7586       0.1937           \[0.0847, 0.3051\]
  ---------------------------------------------------------------------------------------

Panel B: Empirical distribution distances before and after weighting

  -----------------------------------------------------------------------------------
  **Log variable**              **Original KS distance**   **Weighted KS distance**
  ----------------------------- -------------------------- --------------------------
  Auction volume                0.2810                     0.2908

  Total bidders                 0.1080                     0.0364

  Successful bidders            0.0454                     0.0201

  Cover ratio                   0.1142                     0.0579
  -----------------------------------------------------------------------------------

Note: Each weighted comparison retains 643 early and 638 late auctions. The period-membership and outcome models are refitted in 999 three-month block draws. Included-term mean differences are below 1.6×10⁻¹⁵; weight-concentration effective sample sizes are 586.55 and 614.75, not independent temporal sample sizes. KS is the maximum empirical cumulative-distribution distance, not a p-value. Tables S7--S8 provide paired changes and block sensitivities.

Matching the selected moments does not match the full distributions. Log auction-volume KS distance increases from 0.2810 to 0.2908 even though its first and second moments balance; the other three distances decrease. The evidence supports a positive period contrast under this particular moment standardization, not invariance to all composition differences. The volume diagnostic was not used to select a different weight model or sample.

### 4.5 New-time evidence and sensitivity to the nine-month axis

The January--September 2026 sample also shows positive association. Residual correlations are 0.8494 and 0.8350, with slopes 1.3137 and 1.2375. All leave-one-month-out correlations remain positive: 0.8396--0.8626 for A and 0.8230--0.8569 for C. These are same-market, new-period estimates from 166 auctions, not predictive accuracy or a formal test of further strengthening after 2025.

The original block intervals and complete enumeration results are retained in Online Resource 1, Table S9. Non-circular and circular sampling produce different diagnostic percentile ranges; neither expands the nine-month historical record. Accordingly, the additional sample supports the recurrence of the positive direction, with limited evidence about temporal uncertainty. It is not used as a confirmatory replication or as a substitute for the historical sample.

## 5 Discussion

### 5.1 Indicator levels and conditional co-variation

Two economic descriptions of this reporting archive differ. The later historical auctions have lower marginal dispersion ratios but a stronger conditional relationship between the bid-side and award-side measures. Reading only levels would miss the change in co-variation; reading only the pooled regression would hide its historical heterogeneity. Reporting both describes the observed quantities more fully without ranking either period by allocation quality.

The period comparison addresses observed composition only to a specified extent. Positive weighted contrasts remain after selected log-scale means and second moments are balanced, while the auction-volume distribution retains a shape difference. The 2026 exercise addresses a different question: whether the positive direction appears in an additional time segment. It does, but the short segment cannot establish a stable long-run mapping. These exercises narrow the scope of the historical relationship rather than identify why it changed.

This joint characterization complements the quantity moments in official reports and the prices and participation variables examined by Bosco (2023). Its contribution is the magnitude and conditional scope of a report-level relationship, not a new indicator or evidence that official monitoring is mistaken. The denominator checks clarify normalization; they do not remove the inherent link from submitted bids to awards. Nor has this relationship been validated against an independently measured economic outcome.

### 5.2 Identification, inference and data limits

Measurement is the first limit. The standard-deviation populations and variance divisors are not fully documented across the archive, and reporting participants may represent clients. The ratios are arithmetically defined but are not authenticated matched-population inequality measures. Identical labels across files do not establish unchanged statistical populations.

Selection and simultaneity are the second limit. We condition on successful completion, while participation, coverage and awards can share determinants. Reduced controls do not eliminate endogenous selection or unobserved demand conditions. Differences in separately fitted projections may reflect reporting conventions, observed or unobserved composition, and residual scales as well as changes in the underlying relationship. No causal policy, competition or efficiency interpretation follows.

Inference is the third limit. Every interval remains conditional on exploratory choices and an approximate dependence model. The original slope contrasts, secondary correlation contrasts and later weighted contrasts are separate inferential families; no correction covers the entire research history. Exhaustive enumeration removes Monte Carlo variation for its finite set of tuples, not uncertainty about repeated-sample coverage. Circular blocks additionally impose an artificial endpoint link.

External price informativeness is untested. The inspected official report describes a bidding-window-close reference but provides the relevant price comparisons as monthly summaries, not the matched auction-level series required here (European Commission 2023). No eligible external series was obtained, so no price regression was run. This is a data limitation, not a negative price result. Separately, access to the exact 2026 raw snapshot is not secured by its dynamic download URL; the reproducibility boundary is stated below.

## 6 Conclusion

Reported bid and award dispersion are positively associated across 1,281 successful EUA auctions during 2020--2025. The pooled residual correlation is about 0.65 under both transformations, while the later historical period has a stronger relationship despite lower marginal report-ratio medians. The period contrast remains positive after balancing selected composition moments, but the auction-volume distributions remain unequal.

A separate set of 166 auctions in January--September 2026 also has a positive relationship. Its short time axis limits the inferential weight of that observation. Together, the results distinguish levels, co-variation and temporal scope in public quantity reports. They do not establish matched-bidder distributional change, a causal allocation mechanism or operational value.

## Data and computer code availability

The historical input and analysis records are available in repository 124-creator/-123 at the fixed revisions listed in Online Resource 1. The input is fixed at 5745eb3ddca79602346053446583d794b0e09800; main estimates, original robustness and subsequent composition analyses are preserved separately. Integration checks are fixed at 35d8c63fc57173f67eb0bd8bb570eb289188324f under research/eex_integration_checks_20261010. EEX retains its data rights. The 2026 analysis used a 72,742-byte snapshot, identified by its full SHA-256 in Online Resource 1. The download URL is dynamic, and the exact raw file is not included in this replication package. Numerical outputs and code therefore do not by themselves provide complete raw-data reproducibility for the 2026 extension. A lawful exact-snapshot access arrangement remains to be finalized; a later file with a different hash must not silently replace it.

## Statements and Declarations

Funding: The authors received no financial support for this research.

**Competing interests:** \[Both authors must confirm their relevant financial and non-financial interests before submission.\]

**Author contributions:** \[Zhongfei Tian and Xiang Wang must confirm their actual contributions in the separate title-page record; author order is not a substitute for a contribution statement.\]

Author-review status: Xiang Wang has reviewed the preceding manuscript. This revision changes presentation and methodological explanation without new estimation. Outstanding declarations and the exact-snapshot data-access arrangement are recorded in the author checklist.

## Supplementary information

**Online Resource 1 Field dictionary, sample provenance, supplementary estimates, measurement identities, short-axis diagnostics and evidence-status map**

## References

Ausubel LM, Cramton P, Pycia M, Rostek M, Weretka M (2014) Demand reduction and inefficiency in multi-unit auctions. The Review of Economic Studies 81:1366--1400. https://doi.org/10.1093/restud/rdu023

Bosco B (2023) Trade, equilibrium prices and rents in European auctions for emission allowances. Environmental Economics and Policy Studies 25:87--113. https://doi.org/10.1007/s10018-022-00344-y

Cook RD (1977) Detection of influential observation in linear regression. Technometrics 19:15--18. https://doi.org/10.1080/00401706.1977.10489493

Cramton P, Kerr S (2002) Tradeable carbon permit auctions: how and why to auction not grandfather. Energy Policy 30:333--345. https://doi.org/10.1016/S0301-4215(01)00100-8

EEX (n.d.) Frequently Asked Questions: Emissions Auctions. European Energy Exchange. https://www.eex.com/en/faq. Accessed 10 October 2026

European Commission (2023) Auctions by the Common Auction Platform: October, November, December 2023. https://climate.ec.europa.eu/document/download/f3199005-4ca8-461b-9499-e5f3846ea4a5_en?filename=cap_report_202312_en.pdf. Accessed 10 October 2026 (parsed text, Sections 1.1.1 and Annex 2)

European Commission (2024) Auctions by the Common Auction Platform: April, May, June 2024. https://climate.ec.europa.eu/document/download/d962459c-021e-4901-b49f-e5d37e5d2c93_en?filename=cap_report_202406_en.pdf. Access record: 10 October 2026

European Securities and Markets Authority (ESMA) (2025) Market Report on EU carbon markets. ESMA50-481369926-30552. https://www.esma.europa.eu/sites/default/files/2025-10/ESMA50-481369926-30552_Carbon_Markets_Report_2025.pdf. Accessed 10 October 2026

Kronmal RA (1993) Spurious correlation and the fallacy of the ratio standard revisited. Journal of the Royal Statistical Society: Series A 156:379--392. https://doi.org/10.2307/2983064

Lahiri SN (2003) Resampling methods for dependent data. Springer, New York. https://doi.org/10.1007/978-1-4757-3803-2

Li F, Morgan KL, Zaslavsky AM (2018) Balancing covariates via propensity score weighting. Journal of the American Statistical Association 113:390--400. https://doi.org/10.1080/01621459.2016.1260466

Lovell MC (1963) Seasonal adjustment of economic time series and multiple regression analysis. Journal of the American Statistical Association 58:993--1010. https://doi.org/10.1080/01621459.1963.10480682

Meijer E, Postepska A, Wansbeek T (2025) Handling multiple proxies. Empirical Economics 69:2901--2926. https://doi.org/10.1007/s00181-025-02825-x

Niu H, Liu T (2024) Forecasting the volatility of European Union allowance futures with macroeconomic variables using the GJR-GARCH-MIDAS model. Empirical Economics 67:75--96. https://doi.org/10.1007/s00181-023-02551-2
