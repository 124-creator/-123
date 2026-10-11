# E2: bid-quantity dispersion and a matched auction price deviation

Date: 11 October 2026. Status: **conditional design, NOT released for estimation**. A source-specific protocol, exact pair manifest and reference contract must be locked after sample validation and before examining price associations. The already explored historical archive cannot be made preregistered by this document. Keep v8 and all historical estimates unchanged.

## 1. Question and estimand
Does the reported bid-volume SD-to-reported-mean ratio have a conditional association with the signed auction-price deviation beyond established auction quantities, participation and bid-price spread? It is a completed-auction descriptive question, not a forecast, auction-efficiency test, or causal design.

Proposed target: d = 10,000 × (auction clearing price − reference midpoint) / reference midpoint, in basis points. Positive denotes a premium. The reference must concern compatible EUA units and delivery, and be at or immediately before the separately verified bidding-window close. No daily-close proxy, monthly duplication, chart digitization, continuous-December-future substitution or silent quote-kind mixing.

Primary added regressor: x = log(1 + reported bid-volume SD / reported bid-volume mean). Natural log on the same positive sample is a secondary measurement sensitivity; not a second independent discovery. No award-volume dispersion is introduced in this round. Unresolved bidder populations/ddof remain interpretation limits, not reasons to fabricate a population CV.

## 2. Price sample and information rule
Start with the fixed 1,281 successful T3PA EU/DE/PL auctions of 2020–2025. Preserve product, series, date, original file/sheet/row and all exclusion reasons. Neither dependent-variable magnitude nor sign is a qualification criterion. No trimming or winsorization. The fully common analysis sample must be eligible for every locked baseline/extension. An unpaired event remains in the accounting, not as a zero price deviation.

The workbook's Time column has no authenticated deadline semantics; it is never substituted for the deadline. Supply a separate calendar table with per-event closing timestamp and documentary source. Convert timezone-aware timestamps to UTC; the calendar's applicable daylight-saving convention must be documented. A publisher's reference labelled 'at close' can qualify without subsecond provenance if its quote definition, clock rule and per-auction association are unambiguous; finer precision must not be invented.

Prefer one product, one source and a midpoint quote contract for the whole matched sample. Other-source pooling needs a separate pre-analysis justification. Set an age limit only after examining the source's sampling convention, before association results; the software leaves that limit unlocked. A suggested range for a fresh quote is at most 60 seconds, but this is not a universal market or journal standard. Never scan age cutoffs for significance. No fallback from midpoint to trade/bid or missing quotes.

All bid/award statistics are disclosed after completion. Even a reference preceding the close does not make those auction statistics available beforehand. Model results must not be called real-time predictive gains.

## 3. Strong, identical-sample comparison
Baseline Z: log auction volume V, log total bidders N, log successful bidders S, log reported cover ratio R; bid-price spread (maximum minus minimum submitted price, EUR/tCO2); log reference midpoint; reporting-series and year–month indicators. A single-series sample has no redundant series dummy. Raw bid-price spread avoids dividing that control by the dependent variable's reference denominator. Including log midpoint permits price-level scaling; coefficients remain descriptive.

M0: d = Zη + error.
M1: d = Zη + γx + error.
M2: the same as M1 with ordinary log bid dispersion, secondary only.

Fit the same dates and weights (one auction, one weight). Do not let M0 retain dates unavailable to M1/M2. Report design rank and residual degrees of freedom. No automatic ridge fallback when rank is deficient. No new neural networks, model search, residual-based feature choice or award-dispersion branch.

## 4. Magnitude, inference and limited diagnostics
Primary reported quantities: γ, its 95% time-dependence-aware interval, and γ × the IQR of residualized x, in basis points. A residual IQR contrast describes the fitted conditional association, not an intervention. Also show an illustrative EUR/tCO2 conversion at the matched reference-price median, explicitly not an execution gain or arithmetic conditional expectation. Show the implied effect over the observed raw x IQR as secondary scale information, distinguishing the two scales. Recompute sample-estimated IQR/median within each resample when attaching uncertainty to derived quantities.

Partial R-squared is secondary descriptive fit, never proof of added economic information or out-of-sample gain. No fit threshold or p-value defines novelty. Minimum meaningful effect must be discussed in reference-price precision and the market's unit context before interpreting results. A price tick is a measurement context, not automatically a welfare threshold. Until this is set and precision is adequate, do not declare equivalence from nonsignificance.

Proposed main dependence calculation: 999 paired three-calendar-month moving-block draws, all three fits sharing indices and re-estimating nuisance parameters. Preserve month labels and empty months; failures retained, no replacement. One-month and six-month checks use 199 shared draws each and are reported regardless of favourability. These are exploratory approximations, not guaranteed coverage under arbitrary nonstationarity.

Time check: leave each available calendar year out once, report all focal coefficients and IQR effects. It is an influence/stability diagnostic, not a causal break or new prediction experiment. Conduct only if the accepted sample spans at least three years. Do not re-use the already analysed 2026 sample as an untouched test. No economic forecast test with contemporaneous regressors or future month fixed effects.

Proposed computational ceiling: 5,000 fitted models, 15 minutes core compute, one analysis pass. Three point fits + 3×(999+199+199) bootstrap fits = 4,194; at most 18 leave-year fits gives 4,212 before small independent numerical cross-checks. Stop on budget or numerical failure without tuning. These are design limits, not verified power or a journal requirement.

A single monthly sample is for schema validation only. Before releasing inferential analysis, propose at least 200 paired auctions spanning at least 24 months, with at least 100 residual degrees of freedom. These are initial feasibility checks, not sufficient power proofs or universal publication thresholds. Insufficient coverage is reported rather than solved by relaxing the design after seeing effects.

## 5. Release and stop rules
Lock documentary source IDs/hashes, units, contract compatibility, deadline calendar, quote convention/age, permissible use, complete eligibility manifest, primary contrast and code version before fitting. A programmatic schema PASS does not authenticate documents or permission.

If reference access fails or per-auction data are unavailable, stop E2 with zero price estimates and retain the quantity manuscript. If reference data qualify but the effect is small, uncertain or year-specific, retain all results and limit the economic conclusion. Do not change target, source or transform to obtain significance. A precise exclusion of a prespecified economically material association is different from an imprecise null result. Only actual completed results may be integrated into main results/abstract.
