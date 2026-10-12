# Data access and reproduction

Article: Quantity dispersion and reported price deviations in European carbon auctions
Authors: Zhongfei Tian; Xiang Wang. Correspondence: 15517837680@163.com.
Editorial revision: v10.1, 12 October 2026. This file is an access and execution guide, not a new market-data deposit. No market model was fitted for this revision.

## Fixed public releases

| Evidence | Fixed source | Repository directory |
|---|---|---|
| Historical quantity input | [5745eb3d](https://github.com/124-creator/-123/tree/5745eb3ddca79602346053446583d794b0e09800/research/pro_review_20261010/full_data/) | `research/pro_review_20261010/full_data/` |
| Pooled quantity models | [e25c1e02](https://github.com/124-creator/-123/tree/e25c1e02e1a58e0aec1084f7419066855e9565ec/research/eex_abc_results_20261010/) | `research/eex_abc_results_20261010/` |
| Periods, control and influence diagnostics | [d4b26f1b](https://github.com/124-creator/-123/tree/d4b26f1bbd8c1d7c036259e48e119c9c12f6c9a9/research/eex_robustness_20261010/) | `research/eex_robustness_20261010/` |
| Overlap weights and first 2026 estimates | [89d3ac3b](https://github.com/124-creator/-123/tree/89d3ac3beba670838d4b62b1209f6f3412753f19/research/eex_evidence_strengthening_20261010/) | `research/eex_evidence_strengthening_20261010/` |
| Finite 2026 diagnostics | [35d8c63f](https://github.com/124-creator/-123/tree/35d8c63fc57173f67eb0bd8bb570eb289188324f/research/eex_integration_checks_20261010/) | `research/eex_integration_checks_20261010/` |
| German price estimates, exact specifications and stored draws | [fccd471d](https://github.com/124-creator/-123/tree/fccd471de96548bd781c59aced4a59435aae08ac/research/eua_local_price_execution_20261011/) | `research/eua_local_price_execution_20261011/` |
| Price descriptions and source-definition audit | [33707c16](https://github.com/124-creator/-123/tree/33707c164c80accd7acf9fcd3f0965088a8370f6/research/eua_price_description_followup_20261011/) | `research/eua_price_description_followup_20261011/` |

The link targets are fixed historical commits, not the changing default main branch. The present revision does not replace their specifications or estimates. Public availability of an earlier file does not supply a new licence to redistribute it. Respect provider conditions.

## What is public, and what still requires access

The fixed historical-quantity release includes six original XLSX workbooks, INPUT_MANIFEST.json and the parsed eligibility tables. The price release contains the executed code, mapping, protocol, aggregate estimates and stored draw statistics. Existing public availability is not a new licence for third-party data.

The authors hold the German quarterly PDF editions and matched reported-price CSVs. They are not newly deposited here because unrestricted bulk redistribution rights have not been established. A request to the corresponding author should specify the 2020–2025 German reported-price comparison and the required 275-event archive, 240-event primary subset, excluded 35 rows, or 203-row unflagged subset. The author can supply released code and metadata and identify the matching report editions. Any transfer of event-level data or third-party originals remains conditional on provider permissions and use conditions; delivery is not guaranteed by this statement.

SOURCE_CATALOG.md and Online Resource 1 Table S14 identify recorded official report editions. Their links have not all been redownloaded in this editorial revision. Do not silently substitute a changed edition. The exact separate 2026 quantity snapshot is also not publicly deposited: 72,742 bytes, SHA-256 `54e6fb649872d229333adb29b62a3ff5b7fddd7393facc047050fb8f87a1bf3d`. A dynamic URL and hash do not make its matching bytes accessible. Neither that quantity extension nor the separately held 2026 German price observations are added to the 240-row historical price model.

Thus the guide specifies a concrete execution path for someone who has lawfully obtained matching inputs; it does not establish that every external reader can obtain them. Complete independent raw-input reproduction and editorial acceptance of the access arrangement remain separate, unresolved conditions.

## Exact inputs for the historical price analysis

Use a fresh private copy of `research/eua_local_price_execution_20261011/` at fixed commit `fccd471de96548bd781c59aced4a59435aae08ac` as PRIVATE_RUN. Preserve its code, `INPUT_MAPPING.json`, protocol and original lock. Use the historical quantity input directory at `5745eb3ddca79602346053446583d794b0e09800` as EEX_FULL_DATA; the audit consumes its six `raw/*.xlsx` workbooks, `INPUT_MANIFEST.json`, `parsed/extraction_all_2020_2025.csv` and `parsed/candidate_dispersion.csv`.

PRIVATE_FULL24 must contain the following frozen CSVs either under `data/` or directly in that root. Exact byte lengths, checksums and row counts are enforced by the runner, not merely suggested by the filenames:

| File | Rows | Bytes | SHA-256 |
|---|---:|---:|---|
| official_reported_cutoff_all275.csv | 275 | 181495 | b168de79301d99003e95d62779bd75d02a97a34d1b876034f3f26bf23273abed |
| official_reported_cutoff_strict240.csv | 240 | 154561 | 7e12f25db5bb97f3b0152f264519803569edcee9914da548ff156ee7e058f4c1 |
| official_reported_cutoff_excluded35.csv | 35 | 27740 | 7e332bb5be5f1cb1ebb9b83def7d9c2dabc0e846d81de698930de1751e7dbecb |
| official_reported_cutoff_noflags.csv | 203 | 130034 | 7441f31c72b220adb6fc2374d0205f510955023f9f3cb405e6660478a59c6086 |

The literal mapping uses `auction_date`, `auction_price_eur_tCO2`, `reported_deviation_percent_signed` and `reference_event_type`; the signed percentage-point field is multiplied by 100 to obtain basis points. It maps V/B/N/S/mu_B/sd_B/mu_W/sd_W to the eight stated quantity fields and retains `source_report_id`, `source_pdf_sha256`, `source_pdf_relative_path`, `source_pdf_page_1based` and `source_line_literal`. Read the complete mapping rather than guessing headers. The source PDFs are provenance evidence; the fitting runner itself reads the CSVs and the original-derived auction table, not the PDFs.

The runner restricts the audited auction table to DE/T3PA, reconciles dates and subsets, and checks the auction price and eight quantity fields across sources. Coverage R and submitted-price extrema come from the audited auction table, not a nonexistent R column in the reported-price CSVs. The expected auction-table SHA-256 is `b1d737d7dc7d1af53b989560ccb13d8cad52345747441ab34f77c320edbe498f`.

## Existing no-fit check and full-refit commands

Use Python 3.11 and the fixed price release's `requirements.txt`. `REQUIREMENTS_ACTUAL.txt` records the originally exercised environment; it is not a request to install the agent. Set TMPDIR, TEMP and TMP to an authorized local scratch directory, PYTHONDONTWRITEBYTECODE=1, OPENBLAS_NUM_THREADS=1 and OMP_NUM_THREADS=1. On Windows use native forward-slash paths. Replace uppercase placeholders with actual lawful input locations. All output directories below must be new, private directories; the original scripts do not reliably refuse every existing output directory.

From PRIVATE_RUN, the existing no-fit check is:

```bash
python -B code/run_official_reported_price.py --private-root PRIVATE_FULL24 --out private_header_inspection --inspect
```

This validates the four CSVs against the frozen hashes, byte lengths and row counts and records their headers. It does not fit a model, validate cross-source matching or authenticate a provider's statistical definitions. A successful header check must not be called a complete input audit.

For a lawfully equipped independent reproduction, first rebuild and audit the auction table, then execute the fixed specification:

```bash
python -B code/audit_auction_prices.py --input EEX_FULL_DATA --out private_auction_base_reviewed
python -B code/run_official_reported_price.py --private-root PRIVATE_FULL24 --auction-prices private_auction_base_reviewed/auction_prices_local.csv --mapping INPUT_MAPPING.json --out real_results
```

The first command performs source-cell and eligibility checks and creates the private auction table without a regression. The second performs the market fits, including the locked bootstrap and deletion diagnostics. These commands were inspected and their `--help` interfaces exercised for v10.1; the market-data commands were not rerun for this editorial revision. Their historical execution is documented by the fixed price-release records. `verify_actual_results.py` also re-estimates models and is not a no-fit check.

Retain the original source records and read the resulting `EXECUTION_STATUS.json` and `INPUT_GATE.json`; compare a reproduction with the frozen public `results/` files, not by assuming any new output is successful. Never replace unavailable inputs with invented rows, altered hash constants, later vendor editions or zeros. A copied historical prefit lock is not a new preregistration.

## Public presentation checks and historical SI locators

`support/PRICE_RESULTS.json`, `support/PRICE_DESCRIPTIVES.json`, `tables/PRICE_DISPLAY_LEDGER.csv`, figure inputs and the fixed releases support arithmetic and presentation checks. They do not reconstruct missing auction-level observations. The display ledger retains its original v9 document-position convention; use the table numbers visible in the current manuscript. The unchanged SI S8 locator `support/frozen_extension_results.json` refers to the earlier analysis companion; it is not a file newly supplied here. The equivalent period-diagnostic fields are `periods.A.delta_theta_CI95` and `periods.C.delta_theta_CI95` in `research/eex_robustness_20261010/KEY_RESULTS.json` at the fixed period-diagnostics commit above.

## Rebuilding this finite document revision

Install `requirements_editorial.txt` in a separate environment. Create a new empty EDITORIAL_OUTPUT directory and copy this package's `FINITE_REVISION_PLAN.json` into it. Keep the v10 source directory at `30116aa4b230272207ea7818a284f648fa988fb2` unchanged. From the repository root:

```bash
python -B paper/eex_finite_v10_1_20261012/tools/revise_finite.py --source paper/eex_final_v10_20261011 --out EDITORIAL_OUTPUT
```

The editor checks the three source Word hashes, changes only specified plain paragraphs, and checks canonical OfficeMath, table and drawing structures. It copies, rather than regenerates, frozen figures, table ledgers and aggregate records. It is a trusted-local-folder editorial helper, not a hostile-filesystem sandbox or a transactionally atomic multi-file writer. It refuses known existing deliverables; use a genuinely fresh destination.

The new main and title PDFs were exported locally through WPS Office 12.1.0.24655's Word-compatible COM interface. The interface reports the product name “Microsoft Word” and version 14.0, but the observed installation path and PDF creator identify WPS; this is not a Microsoft Word execution certification. The unchanged SI Word and PDF files are retained byte-for-byte from v10. Re-render after future edits and inspect the pages; pagination and document metadata need not be identical across rendering environments. The historical v9 subject metadata inherited by the main Word/PDF is not the version authority; use this directory, plan and Git commit.
