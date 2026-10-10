# Integration checks and missing-price gate — 2026-10-10

The user authorized official-source retrieval, bounded supplementary experiments and integration into the manuscript. Existing 2020–2025 and 2026 E3 results are already known. This is a POST-RESULT sensitivity diagnostic, not preregistration or an independent confirmatory experiment. Do not replace old results, tune for significance, contact third parties, buy data or republish raw sources.

## E2: bounded official-source follow-up
A newly accessible European Commission Q4 2023 report was read through the official PDF text service. Section 1.1.1 describes a monthly auction-price minus closing-window EEX spot midpoint comparison; Annex 2 contains individual auction-price/bid-price/quantity columns. Read these as distinct levels. Monthly external-price summaries cannot populate individual-auction rows. The official 2025Q2 PDF returned 429 and is not retried. Previous blocked DEHSt and EC reports are not retried through alternative tools.

Permit one direct download of the SAME accessible Q4 2023 official PDF on the runner after container transport failure; this is not an HTTP-denial workaround. Save a source receipt and a compact column-level inspection, not full third-party text or raw bytes in the public repository. If no individual external reference price and timestamp are supplied, E2 remains HOLD and price regressions remain zero. No surrogate daily close, digitization or bidder-price proxy.

## E3R: finite resampling and endpoint sensitivity
The prior E3 file has SHA-256 54e6fb649872d229333adb29b62a3ff5b7fddd7393facc047050fb8f87a1bf3d and 72742 bytes. Retrieve the same official 2026 annual URL once. If the current bytes differ or headers/eligibility differ, stop E3R as HOLD rather than substitute a new snapshot. Eligibility remains successful T3PA EU/DE/PL auctions from 2026-01-01 through 2026-09-30, with 166 observations expected as a consistency check, not a filtering target.

The earlier 999-draw percentile intervals are based on nine months and only seven possible non-circular three-month block starts. Diagnose the finite distribution and endpoint choice; do not use more bootstrap draws to claim more independent observations.

1. Re-estimate the two original A/C projections once; match frozen E3 points to 1e-9.
2. Enumerate all 7^3=343 ordered triples of non-circular three-month blocks. Each tuple has equal mass. Keep original year–month labels; all auction rows in each selected month share multiplicity. Re-estimate both projections for every tuple.
3. Enumerate all 9^3=729 ordered triples of CIRCULAR three-month blocks. Wrap September to January explicitly. This equalizes marginal month inclusion but imposes artificial end-to-start adjacency; it is a competing assumption, not an automatically superior method.
4. Delete each of nine months once for each A/C specification; retain the original main sample and treat ranges as influence diagnostics, not confidence intervals.
5. For every design report theta/beta 2.5%, median and 97.5% quantiles with linear interpolation, failures, distinct multiplicity vectors and expected month counts. The finite distribution is enumerated exactly; inferential coverage is NOT exact or confirmed. Keep the old Monte Carlo intervals unchanged and label all new results as diagnostics. Do not run a 2026-versus-earlier-period significance test.

Budget: 2 baseline + 2*343 + 2*729 + 2*9 = 2164 projection requests; at most 2300 including cross-checks, and five minutes core compute. Reuse only statically reviewed numerical helpers; no old model/notebook deserialization. Check fixed positive-weight cases against explicit-dummy least squares and compare enumeration mass/count identities on synthetic arrays. All failures retained; no replacement draws or alternative tuning.

## Manuscript integration
Keep historical N=1281 separate from new-time N=166. E1 selected-moment balance and the failed auction-volume distribution diagnostic must be reported together. Preserve E3 short-axis limitations and E2 missing-reference status. Retain corrected whole-word Word subscripts, no-funding declaration, and Xiang Wang's reviewed status for the previous version. New integrated text is an author-review revision, not automatic renewed approval or journal submission. No acceptance probability or CAS qualification is inferred from formatting.