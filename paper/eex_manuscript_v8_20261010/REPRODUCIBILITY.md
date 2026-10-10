# Versioned sources and editorial reproduction

This version does not fit a statistical model. The DOCX objects are edited from v7, with original equations, images and table content protected by checks.

## Document build

From the repository root:

```bash
python paper/eex_manuscript_v8_20261010/tools/revise_v8.py --source paper/eex_manuscript_v7_20261010 --out paper/eex_manuscript_v8_20261010 --plan paper/eex_manuscript_v8_20261010/REVISION_PLAN.json
```

Required versions: python-docx 1.2.0; lxml 6.1.1. The three source DOCX SHA-256 values and exact paragraph text hashes are checked before editing. Markdown is an export for reading, not the build source. Do not rebuild the repaired inline equations through an older Markdown/Pandoc route.

## Statistical evidence, unchanged

Repository: 124-creator/-123.

| Evidence | Fixed commit | Repository directory |
|---|---|---|
| Historical input | 5745eb3ddca79602346053446583d794b0e09800 | research/pro_review_20261010/full_data/ |
| Pooled A/B/C | e25c1e02e1a58e0aec1084f7419066855e9565ec | research/eex_abc_results_20261010/ |
| Initial robustness/periods | d4b26f1bbd8c1d7c036259e48e119c9c12f6c9a9 | research/eex_robustness_20261010/ |
| Overlap weights and initial 2026 | 89d3ac3beba670838d4b62b1209f6f3412753f19 | research/eex_evidence_strengthening_20261010/ |
| Finite 2026 diagnostics | 35d8c63fc57173f67eb0bd8bb570eb289188324f | research/eex_integration_checks_20261010/ |

The source locators above are the route to model reproduction. This editorial package is not a new complete raw-data deposit. Its tables/DISPLAY_NUMERICS_V8.csv records displayed tokens and positions, not independent numerical certification. Original v7 ledgers and support outputs remain in the preceding companion package and fixed research directories.

The 2026 annual URL is dynamic. The required source was 72742 bytes with SHA-256 54e6fb649872d229333adb29b62a3ff5b7fddd7393facc047050fb8f87a1bf3d. It is not included here. Without access to matching lawful bytes, exact raw-data reproduction of that extension remains incomplete; a hash is not an archive. E2 has no fitted price result.


## Repository and companion package
The GitHub manuscript directory contains the reviewed manuscript, editable documents, figures, editorial plan, builder and QA receipts. The complete companion ZIP additionally carries copies of earlier frozen aggregate JSON and CSV outputs. They are not new estimates. Statistical reproduction uses the fixed research commits above; raw market workbooks are not republished here.
