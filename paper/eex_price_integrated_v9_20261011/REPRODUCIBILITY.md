# Versioned integration and reproducibility

## Protected sources

Repository: `124-creator/-123`.

| Object | Fixed revision | Directory |
|---|---|---|
| Manuscript source | 955f694ccc76396e5af90166da8a921cd210a104 | paper/eex_reported_price_v8_2_20261011 |
| Actual price fits | fccd471de96548bd781c59aced4a59435aae08ac | research/eua_local_price_execution_20261011 |
| Price descriptions/definition record | 33707c164c80accd7acf9fcd3f0965088a8370f6 | research/eua_price_description_followup_20261011 |
| Report source index | 6cd665873c9bb11ed266bb3d5eea7e587ef2ca80 | research/eua_official_cutoff_pilot_20261011 |

No private row inputs are included or required for this editorial build. Market reproduction still requires the held reported-price rows and source files, under an appropriate access arrangement. Public identities and aggregate checks cannot substitute for access to those bytes. Original quantities, weights, 2026 diagnostics and their version limits remain documented in Online Resource 1.

## Commands

Materialize the pinned directories above into `PUBLIC_ROOT`, without executing their market scripts. Set SOURCE to the pinned v8.2 directory and OUT to a **new** v9 directory.

```sh
python tools/audit_public_evidence.py --root "$PUBLIC_ROOT" --out "$AUDIT_JSON"
python tools/build_integrated_v9.py --source "$SOURCE" --public-root "$PUBLIC_ROOT" --out "$OUT" --plan REVISION_PLAN.json
python tools/finalize_delivery.py --paper "$OUT" --public-root "$PUBLIC_ROOT" --audit "$AUDIT_JSON"
```

Use Python 3.11+ with python-docx 1.2.0, lxml 6.1.1, NumPy 2.3.5, SciPy 1.17.0; Markdown export uses Pandoc 3.1.11.1. Local rendering uses the supplied document rendering workflow and LibreOffice; the GitHub workflow exports PDF with LibreOffice. Word source content, not PDF pixels or page counts on other software, is the portable evidence object.

Do **not** reconstruct repaired DOCX formulas from Markdown. The DOCX builder checks exact input hashes, protects all old mathematics and table values, and adds the new price equation natively. Markdown is a readable derivative; its title is explicitly restored after export. Existing figure bytes are copied, not re-estimated or redrawn.

`tables/PRICE_NUMERIC_SOURCE_LEDGER.csv` maps numeric values to fixed JSON paths. `tables/DISPLAY_NUMERICS_V9.csv` is a display inventory, not independent statistical authentication. `support/AGGREGATE_AUDIT.json` records the separate arithmetic checks. `support/DOCUMENT_QA.json` and `PRESENTATION_QA.json` concern document integrity only. The publication receipt records the actual remote build and readback.
