# Local price-extension protocol: first-fit decision

This document is written before the first new official-reported price regression in this local session. It is a disclosed exploratory amendment, not a preregistration or untouched test. Old manuscripts and quantity estimates are not modified.

## Version authority and discrepancy

The user supplied a Pro completion message describing 30 synthetic tests, six leave-year-out estimates and a quarter jackknife. The sandbox ZIP in that message was not found in the searched accessible local directories. A real remote branch was fetched at commit 955f694ccc76396e5af90166da8a921cd210a104, branch eex-reported-price-design-20261011. Its actual code has 17 tests, omits both deletion diagnostics, includes log auction price in the baseline, and reports a residualized-x IQR. It is NOT certified byte-identical to the sandbox delivery. The earlier claim of no GitHub commit is no longer an adequate description of the observed remote state.

The implementation here uses the fetched, reviewed numerical core, makes the actual-input correction below, and implements the two bounded diagnostics requested in the user's supplied newer text. These choices are fixed before viewing any estimated market coefficient. No result-driven variable selection is authorized.

## Input and estimand

Four original CSV files retain their exact frozen hashes, sizes and membership: all275, strict240, excluded35 and noflags203. The requested 56-member original ZIP was rehashed and CRC-checked and matches the hash provided by Pro. Dates and prices and eight shared quantity fields must reconcile with the freshly rebuilt original EEX annual-workbook extraction. The price CSV has B (bid volume), not R (reported coverage); B is therefore cross-checked as the eighth shared quantity. R remains an estimation control sourced directly from the separately verified original EEX table, not inferred from an absent CSV column and not replaced with B/V.

Main sample: 240 German successful EUA auctions, 21 report quarters. The 35 quarantined auctions are not reintroduced. The 2026 H1 22-row extension remains separate and is not analysed in this run, avoiding an additional unplanned specification.

Main outcome: reported signed numeric percentage points multiplied by 100 to basis points. Printed zero remains zero. Signed EUR differences are not made positive. The outcome is not a reconstructed midpoint, executable discount, native tick, or independently authenticated event-time price.

Focal regressor: log1p(reported bid quantity SD / reported bid quantity mean). Unknown SD population/divisor remains a limitation; do not call this corporate concentration or a fully authenticated within-population CV.

Fixed baseline: intercept, log auction volume, log total bidders, log successful bidders, log reported coverage, maximum-minus-minimum submitted price in EUR, log auction price, observed-year fixed effects, and reference-last-trade indicator when it varies. Retaining log auction price follows the actual written remote protocol; the short pasted reply did not enumerate it. These are same-auction descriptive controls, not exogenous causes. The extension adds only the focal regressor, on exactly the same rows as its baseline.

## Fixed estimates and inference

Primary: signed outcome, 240 rows. Three secondary specifications only: absolute outcome on the same 240, signed outcome on noflags203, signed outcome on best-bid236. Each has one baseline and one extended fit.

Report quarter-cluster CR1 covariance, finite factor G/(G-1)*(n-1)/(n-k), and t(G-1) 95% intervals. Perform one primary restricted-null wild-cluster t test with 999 Rademacher draws, SeedSequence([20261011,2,240]), no replacements, and two-sided plus-one p. Store signs and draw statistics. Failures invalidate a complete-bootstrap claim. The CR1 interval is not a bootstrap interval.

Primary-only additional diagnostics from the user's supplied Pro text: delete each of the 21 quarters once, and delete each of the six years once. Rebuild only observed-year fixed effects after deletion and omit a constant reference indicator; retain every economic control. Stop on rank deficiency, never drop substantive controls to obtain a favourable estimate. Quarter jackknife is explicitly mean-centred CV3J: variance (G-1)/G * sum((beta_minus_g - mean(beta_minus_g))**2); interval is beta_full +/- t(G-1)*SE. This is not the full-centred CV3 variant. Year deletions are point-estimate influence diagnostics, not six new significance searches or proof of stability.

Main magnitude display: coefficient times IQR of observed focal x, with the corresponding CR1 interval. Preserve the fetched version's residualized-x IQR contrast separately and label it distinctly. Neither contrast is a feasible intervention or causal benefit.

All four configurations retain effect sizes, intervals, partial R-squared, conditioning and focal-quarter-information diagnostics. Do not select an uncertainty procedure after seeing results, and do not present an increase in in-sample R-squared as predictive validation.

## Budget, tests and stopping

Expected estimation calls: 1034 = eight baseline/extended calls + 999 bootstrap calls + 21 quarter deletions + six year deletions. Hard limits remain 1100 estimation calls and 900 seconds, with an external subprocess timeout. Independent numerical verification may replay the four fixed extended regressions only and must be counted separately; no second bootstrap run or additional specification search.

Artificial implementation tests are separate from real market fits. The remote 17 tests were actually run in normal and optimized Python. Local tests expose and then correct the nonexistent R mapping, hashed-buffer reading/short-row refusal, deletion fixed-effect rank issue, and diagnostic formulas. Actual test counts come from execution logs, not the pasted Pro claims.

Input hashes must remain unchanged after execution. Reuse neither old models nor prior regression results. Publish only self-authored code, mapping, method decisions and aggregate empirical outputs; keep raw reports, quote rows and per-auction fitted/residual values local. Failed runs, code changes and timing remain recorded. A successful program does not certify journal acceptance, statistical power, cross-quarter independence, causal interpretation or publication rights.
