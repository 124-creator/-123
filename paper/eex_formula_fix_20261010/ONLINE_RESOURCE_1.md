# Online Resource 1

## Bid and award dispersion in European carbon auctions

*Conditional association and temporal heterogeneity, 2020–2025*

**Journal:** Empirical Economics (intended submission; not yet submitted)  
**Authors:** Zhongfei Tian; Xiang Wang  
**Affiliation:** Zhengzhou University of Aeronautics, Zhengzhou, Henan, China  
**Corresponding author:** Zhongfei Tian, 15517837680@163.com  
**Version:** Author-review v6, 10 October 2026

### S1 Purpose and fixed numerical record

This resource supports the main article with a field dictionary, the completed sensitivity results, reproduction details and measurement identities. All regression estimates and intervals are transcribed from the fixed principal and extension outputs. The manuscript revision introduces no new fit, resampling draw, sample restriction or dataset. Table S5 was calculated in v4 from the same frozen input and is reproduced without recalculation here. Figures 1–3 reorganize existing summaries; Table S6 retains the control-set values moved from the v4 main text. The two distinct transformations are A (log-one-plus reported ratios) and C (natural-log reported ratios). The planned positive-sample log-one-plus specification B equals A because both standard deviations are positive for every selected auction.

The repository is `124-creator/-123`. The input is fixed at commit `5745eb3ddca79602346053446583d794b0e09800`. The principal results are fixed at `e25c1e02e1a58e0aec1084f7419066855e9565ec`, and the robustness extension at `d4b26f1bbd8c1d7c036259e48e119c9c12f6c9a9`. The respective paths are:

- `research/pro_review_20261010/full_data/`
- `research/eex_abc_results_20261010/`
- `research/eex_robustness_20261010/`

The first path contains the raw-workbook identifiers, complete extraction, candidate sample, exclusions and cell traces. The latter two contain the analysis code, protocols, result summaries and receipts. Reproduction should start from the fixed input and rebuild the eligibility rules, not filter until the reported sample size is reached. Data rights remain with the original provider; final journal deposit or access arrangements require author confirmation.

### S2 Fields, observations and eligibility

**Table S1 Reported fields and research interpretation**

| Symbol | Original field label | Interpretation retained here |
|---|---|---|
| $\mu^b$ | Average volume bid per bidder | Reported bid mean |
| $s^b$ | Standard deviation of bid volume per bidder | Reported bid SD; population and divisor unresolved |
| $\mu^w$ | Average volume won per bidder | Reported award mean |
| $s^w$ | Standard deviation of volume won per bidder | Reported award SD; population and divisor unresolved |
| $V$ | Auction Volume tCO2 | Reported quantity, not a separately observed settlement total |
| $B$ | Total Amount of Bids | Total reported bid volume |
| $R$ | Cover Ratio | Reported demand coverage |
| $N$ | Total Number of Bidders | Participants, not number of submitted orders |
| $S$ | Number of Successful Bidders | Successful participants, not number of successful orders |

*Note:* Quantity fields use tCO2 in the source. Literal labels are reproduced from row 6 of Primary Market Auction in each annual workbook. In particular, column M is “Total Amount of Bids” within the volume section; auction revenue is a different field. Original labels, cell positions and formats are retained in the provenance record. A reporting participant need not equal a final client or compliance installation. Field labels and arithmetic consistency do not establish identical populations for each paired mean and standard deviation.

The six annual files yield 1,327 dated observations. Restricting to T3PA, EU/DE/PL and explicit successful status yields 1,281 unique auctions. Exclusions comprise 38 other-product records, five other-series records and three cancelled auctions. Cancelled award fields remain missing rather than becoming zero dispersion. No main-sample row is removed on the basis of the size of its reported ratio.

The source audit compared 13 numeric fields for all dated observations with the extraction and the cell trace, with 17,251 comparisons in each route. An independent XML route agreed with the workbook import. The 53 candidate fields match their corresponding extraction rows; input files were unchanged after computation. These checks certify the relationship between the supplied files and the calculations, not unobserved bidder identities, every market event or historical first-release values.

### S3 Projection and resampling implementation

The main nuisance space contains log cover ratio, log auction volume, log total bidders, log successful bidders, reporting-series indicators and original year–month indicators. Each auction has equal weight. Numerically stable least-squares projection gives a rank-79 pooled design with 1,202 residual degrees of freedom. The within-month implementation was cross-checked using an explicit dummy design and explicit row replication on fixed draws. Such agreement verifies a numerical route, not a second empirical sample.

For pooled block length $L$, draw starting months uniformly from $0,\ldots,M-L$ with $M=72$. Append each selected contiguous block of $L$ calendar months until at least 72 positions are obtained, then truncate. Retain all auction-series observations in each selected month. Multiplicities act as observation weights; original year–month labels are not renamed. Empty factor levels in a draw are removed rather than represented by all-zero dummy columns. Nuisance coefficients and the focal coefficient are re-estimated in each draw, and failures are recorded without replacement draws.

The principal stream uses `SeedSequence([20261010, block_length])`. The three-month analysis uses 999 draws shared across A/B/C; the one- and six-month checks use 199 each for A and C. Quantiles are computed by linear interpolation. The prior team calculation used a different initialization; this resource retains the frozen principal intervals rather than the more favourable of alternative Monte Carlo realizations. In particular, the principal ordinary-log slope interval includes one.

For the historical split, each original half has 36 months. Independent three-month resampling within each half produces 999 paired comparisons, shared across A and C. The extension protocol records the period stream `[20261010, 2, 1]`, the reduced-control stream `[20261010, 2, 2]` and the series stream `[20261010, 2, 3]`. All nuisance slopes are separately estimated in each half. The two 97.5% slope-difference intervals constitute a Bonferroni-style sensitivity calculation only to the extent that each interval approximation is adequate. They do not correct selection of the historical question or fully represent cross-boundary dependence.

Reduced-control specifications use 499 draws, and within-series analyses use 399. Each subseries retains the full 72-month calendar axis, including months without selected auctions. EU and PL each have one such empty month. No observation is fabricated there. Singleton months contribute no net within-month information. The completed runs report no failed bootstrap draw. Bootstrap coverage remains approximate, particularly under changes in slopes or dependence.

### S4 Additional numerical results

**Table S2 Pooled block-length sensitivity**

| Spec. | Block months | Draws | $\beta$: 95% interval | $\theta$: 95% interval |
|---|---:|---:|---|---|
| A | 1 | 199 | [0.7807, 0.9833] | [0.5903, 0.7158] |
| A | 3 | 999 | [0.7506, 1.0384] | [0.5714, 0.7422] |
| A | 6 | 199 | [0.7350, 1.0292] | [0.5564, 0.7438] |
| C | 1 | 199 | [0.7907, 0.9714] | [0.5855, 0.7134] |
| C | 3 | 999 | [0.7627, 1.0143] | [0.5660, 0.7402] |
| C | 6 | 199 | [0.7503, 1.0090] | [0.5526, 0.7493] |

*Note:* These are exploratory percentile intervals. Three-month rows reproduce the principal result; they are not additional replications. Sensitivity endpoints based on 199 draws have non-negligible Monte Carlo variability.

**Table S3 Influence sensitivity of residual correlation**

| Deletion diagnostic | A: $\theta$ range / value | C: $\theta$ range / value |
|---|---|---|
| One calendar month | [0.6419, 0.6656] | [0.6405, 0.6674] |
| One calendar year | [0.6058, 0.6981] | [0.6023, 0.6996] |
| One reporting series | [0.6019, 0.7120] | [0.6110, 0.7081] |
| One observation | [0.6467, 0.6569] | [0.6457, 0.6577] |
| Top 13 Cook-distance rows | 0.6911 | 0.6930 |

*Note:* Bracketed values are deterministic deletion ranges, not confidence intervals. The largest-Cook-distance set is selected within each specification only for diagnosis. It does not define a revised data-cleaning rule. All main estimates retain 1,281 auctions.

**Table S4 Within-series residual association**

| Spec. | Series | $n$ | Residual df | $\theta$ [95% interval] |
|---|---|---:|---:|---|
| A | EU | 840 | 764 | 0.6898 [0.6283, 0.7585] |
| A | DE | 275 | 198 | 0.5619 [0.4567, 0.6808] |
| A | PL | 166 | 90 | 0.8076 [0.6943, 0.8828] |
| C | EU | 840 | 764 | 0.6839 [0.6159, 0.7587] |
| C | DE | 275 | 198 | 0.5689 [0.4679, 0.6870] |
| C | PL | 166 | 90 | 0.8138 [0.7005, 0.8850] |

*Note:* Each series has its own month effects and numeric controls. Intervals use 399 three-month block draws. These are not independent-market replications or formal tests that series coefficients differ. The small PL residual sample limits interpretation.

The interquartile-scale contrasts reported in the main article are already present in the frozen extension output. Under A, $\operatorname{IQR}(M_Zx)=0.0927037454$ and the corresponding fitted transformed-response contrast is 0.0816007553. Under C, these values are 0.1600483679 and 0.1407987656. They are partial-regression scale summaries. Exponentiating a transformed fitted value would not, without further assumptions, recover the arithmetic conditional mean of the original ratio. No such raw-scale mean or procurement outcome is estimated here.

### S5 Denominator identities and rounding

For this diagnostic only, a superscript c labels constructed fields. Define $\mu^{b,\mathrm{c}}=B/N$, $\mu^{w,\mathrm{c}}=V/S$ and $R^{\mathrm{c}}=B/V$, retaining $V$ as the reported auction-volume field. For positive components,

$$
\log r^{b,\mathrm{c}}=\log s^b+\log N-\log R^{\mathrm{c}}-\log V,\qquad (S1)
$$

$$
\log r^{w,\mathrm{c}}=\log s^w+\log S-\log V.\qquad (S2)
$$

If the common nuisance space $\mathbf Z^{\mathrm{c}}$ contains these constructed log totals and counts, linear projection gives

$$
M_{Z^{\mathrm{c}}}\log\mathbf r^{b,\mathrm{c}}=M_{Z^{\mathrm{c}}}\log\mathbf s^b,\qquad
M_{Z^{\mathrm{c}}}\log\mathbf r^{w,\mathrm{c}}=M_{Z^{\mathrm{c}}}\log\mathbf s^w.\qquad (S3)
$$

The completed calculation yields maximum residual discrepancies of approximately $7.47\times10^{-15}$ and $7.09\times10^{-15}$. These are algebraic and implementation checks, not another economic finding. They do not supply an independently observed total award $W$ or authenticate $V=W$.

With the original reported rather than constructed values, mean discrepancies relative to $B/N$ and $V/S$ reach 0.5 quantity units, while the cover-ratio discrepancy relative to $B/V$ reaches approximately 0.004994. Agreement with display precision is not certification of the historical rounding rule. The main regressions use the reported fields; neither implied means nor implied cover ratios silently replace them. The corresponding log-one-plus terms do not satisfy the additive log identities.

A related interpretation boundary concerns concentration. If $m$ quantities genuinely form one population with common mean $\mu$ and $s^2=\sum_i(q_i-\mu)^2/(m-d)$, then its single-auction quantity-share concentration is

$$
H=\frac{1}{m}+\frac{m-d}{m^2}\left(\frac{s}{\mu}\right)^2.\qquad (S4)
$$

This conditional moment identity is standard algebra. It does not justify substituting $N$ or $S$ when the standard-deviation population is unknown. Cross-auction concentration additionally requires identity links across auctions. The current study neither computes a certified bidder-population concentration index nor infers matched-population compression from its cross-auction regression.

### S6 Exploration record and author responsibilities

The snapshot, target and some results were inspected before the supplementary protocols were fixed. The first-freeze record is partial. The manuscripts and intervals cannot therefore be described as preregistered, selection-adjusted or based on an untouched test sample. The principal and robustness outputs are frozen for the current revision; no result was recomputed to make the text more favourable.

An earlier supplementary protocol proposed 0.10 as an exploratory reference for the absolute standardized association. It was introduced after earlier results were known and is not an economic-cost or journal threshold. It is not used as a decision boundary in the article's figures or as proof of publication value. This presentation change leaves the numerical record unchanged.

The numerical reimplementations use the same archive and are not independent-market replications. Fitting counts are execution bookkeeping, not sample sizes. The scope of the evidence is reported-field association conditional on successful auctions. Author order and the corresponding contact have been supplied for this revision. The corresponding author has confirmed no financial support and Xiang Wang's manuscript review. Other author declarations and data permissions remain separate matters.


### S7 Interpretation of the fitted quantities

All quoted coefficients, intervals and contrasts in the article come from the frozen principal and extension outputs. Residual correlation is a symmetric in-sample statistic; the chosen direction of the regression is not evidence of temporal transmission. With one added regressor and identical residualization, partial $R^2$ equals the square of the residual correlation. These two numbers are not independent confirmations.

The reported fitted contrasts across the interquartile range of residualized bid dispersion remain on their respective transformed-response scales. No back-transformed conditional arithmetic mean, representative bidder outcome or monetary benefit is inferred from them. Subperiod slopes and correlations use separately estimated nuisance coefficients and residual variances. Their difference is a descriptive historical comparison, not a structural invariance test robust to arbitrary changes in reporting or covariate distributions.


### S8 Descriptive context and direct correlation contrasts added to the presentation

**Table S5 Descriptive statistics by historical period**

*Panel A: 2020–2022, n = 643*

| Variable | Mean | Q1 | Median | Q3 | Min. | Max. |
|---|---:|---:|---:|---:|---:|---:|
| Bid ratio $r^b$ | 1.532 | 1.345 | 1.520 | 1.712 | 0.874 | 2.622 |
| Award ratio $r^w$ | 1.459 | 1.247 | 1.443 | 1.629 | 0.443 | 2.707 |
| Cover ratio $R$ | 1.864 | 1.530 | 1.790 | 2.100 | 1.010 | 3.770 |
| Auction volume $V$ | 2.692 | 2.363 | 2.515 | 3.082 | 0.972 | 6.399 |
| Submitted volume $B$ | 4.844 | 3.887 | 4.761 | 5.588 | 1.937 | 12.899 |
| Total bidders $N$ | 22.379 | 20 | 22 | 25 | 12 | 31 |
| Successful bidders $S$ | 16.687 | 14 | 17 | 20 | 3 | 27 |

*Panel B: 2023–2025, n = 638*

| Variable | Mean | Q1 | Median | Q3 | Min. | Max. |
|---|---:|---:|---:|---:|---:|---:|
| Bid ratio $r^b$ | 1.275 | 1.108 | 1.255 | 1.429 | 0.847 | 1.896 |
| Award ratio $r^w$ | 1.384 | 1.184 | 1.356 | 1.557 | 0.665 | 2.295 |
| Cover ratio $R$ | 1.785 | 1.550 | 1.710 | 1.980 | 1.080 | 3.780 |
| Auction volume $V$ | 2.659 | 2.147 | 3.035 | 3.245 | 0.970 | 3.350 |
| Submitted volume $B$ | 4.588 | 4.076 | 4.712 | 5.156 | 1.946 | 6.731 |
| Total bidders $N$ | 22.948 | 21 | 23 | 25 | 15 | 30 |
| Successful bidders $S$ | 17.071 | 15 | 17 | 20 | 5 | 27 |

*Note:* These previously tabulated summaries use the unchanged eligible auctions and equal row weights. Volume fields are in million tCO2; bidder counts and ratios are on their original scales. Quartiles use linear interpolation at (n−1)q (type 7). No p-values, distributional-equality tests, trimming or new regression are introduced. These are marginal auction-level summaries; the early and late auctions do not represent matched bidder populations. Lower marginal ratios cannot be equated with a decline in identified bidder-level inequality, and the table does not explain the change in conditional association.

The direct differences in correlation in main Table 4, Panel C, already exist in the frozen extension: `period_intervals.A.delta_theta_CI` and `period_intervals.C.delta_theta_CI` in `support/frozen_extension_results.json`, and equivalently `periods.A.delta_theta_CI95` and `periods.C.delta_theta_CI95` in the repository's `KEY_RESULTS.json`. The point differences are 0.2296942521 and 0.2305336591. These are secondary exploratory 95% intervals, not the 97.5% primary slope intervals. Displaying them now does not retrospectively change the extension protocol.

The unified numeric ledger is `tables/NUMERIC_LEDGER_V6.csv`. The descriptive calculation was completed in v4; its checks remain recorded in `support/DESCRIPTIVE_RECEIPT.json`. The preserved JSON/CSV supply Table S5 and main Table 2 in this revision. The manuscript package does not claim to contain the original v4 raw-data generator. This v6 package preserves the descriptive JSON/CSV bytes and verifies displayed values without rerunning that script. No new regression, resampling, descriptive calculation or group-difference test was performed.


### S9 Conditioning-set values accompanying Figure 2

**Table S6 Residual association across conditioning sets**

| Conditioning set | A: $\widehat\theta$ [95% interval] | C: $\widehat\theta$ [95% interval] |
|---|---|---|
| Series and year–month effects | 0.6243 [0.5596, 0.7067] | 0.6197 [0.5494, 0.7017] |
| Effects + volume + total bidders | 0.6289 [0.5626, 0.7094] | 0.6239 [0.5521, 0.7044] |
| Full controls | 0.6496 [0.5714, 0.7422] | 0.6486 [0.5660, 0.7402] |

*Note:* Reduced-control intervals use 499 three-month block draws. The full-control row reuses the 999-draw principal intervals. Each conditioning set defines a different descriptive projection; these are not instruments or randomized comparisons.

The table and Figure 2 use the same frozen values. The full-control row duplicates the principal estimate for orientation; it is not an additional empirical result. Figure 1 uses quartile ranges rather than inferential intervals; Figures 2 and 3 use the explicitly stated exploratory confidence intervals. These three uncertainty or dispersion objects must not be interchanged.
