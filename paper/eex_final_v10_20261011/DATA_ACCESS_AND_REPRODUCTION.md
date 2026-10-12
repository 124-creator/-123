# Data access and reproduction

Article: Quantity dispersion and reported price deviations in European carbon auctions
Authors: Zhongfei Tian; Xiang Wang. Correspondence: 15517837680@163.com.
Editorial date: 11 October 2026. This file is a locator and access statement, not a new market-data deposit.

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

## Inputs that are not included

The authors hold the German quarterly PDF editions and matched reported-price tables. Their unrestricted redistribution has not been authorized. A request to the corresponding author should identify the German 2020–2025 official-reported comparison and whether the 275-event archive, 240-event primary subset, or a source-restricted subset is required. The author can identify relevant source editions and discuss the applicable access conditions. Provision of any restricted table or original remains conditional on provider permission; this is not an unconditional promise of delivery.

The report links in `SOURCE_CATALOG.md` and Online Resource 1 Table S14 identify official editions recorded by the project. These links have not all been redownloaded for this editorial revision. A later response with a different hash is not silently substituted for the frozen edition. The exact 2026 quantity snapshot (72,742 bytes; SHA-256 `54e6fb649872d229333adb29b62a3ff5b7fddd7393facc047050fb8f87a1bf3d`) is not publicly deposited in this package. Its dynamic URL and hash alone do not make the exact bytes available.

## Reproducing results versus checking their presentation

For statistical reproduction, start with the original scripts and exact input requirements in the linked research release. Private input files are required for a fresh German price refit. The public `PRICE_RESULTS.json`, `PRICE_DESCRIPTIVES.json`, stored audit receipt and display ledger permit arithmetic and editorial checks, but are not synthetic substitutes for event observations. No price or quantity model was fitted for v10.

The SI S8 locator `support/frozen_extension_results.json` refers to the earlier analysis companion. This v10 package does not duplicate that historical file. Its stated equivalent is `research/eex_robustness_20261010/KEY_RESULTS.json` at the fixed period-diagnostics commit above (`periods.A.delta_theta_CI95` and `periods.C.delta_theta_CI95`). Newly integrated price display values are in this package's `tables/PRICE_DISPLAY_LEDGER.csv`; the ledger was inherited from v9 and must be read with its original document-position convention. `support/FINAL_QA.json` and `TABLE_NUMBER_MAP.json` document the v10 editorial reordering.

## Rebuilding the documents

Use Python 3 with python-docx, lxml and matplotlib. From a repository that contains the unchanged v9 directory:

```bash
python paper/eex_final_v10_20261011/tools/build_price_figure.py --root paper/eex_final_v10_20261011
python paper/eex_final_v10_20261011/tools/revise_v10.py --source paper/eex_price_integrated_v9_20261011 --out paper/eex_final_v10_20261011
```

The builder verifies the v9 Word hashes and preserves the mathematical token sequences and table-cell values. The original native formulas, not the Markdown export, are the source. Re-render the generated Word files before use. Exact DOCX metadata bytes and page breaks can differ across word processors; no Microsoft Word/WPS native execution is certified here.
