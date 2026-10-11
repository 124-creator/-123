# Editorial reproduction of v10

This revision changes organization, prose, typography and author-confirmed declarations, not empirical specifications or numerical results. The build source is the exact repaired v9 DOCX at commit35f6b780561907b4914e61e68b0962645ace8e71. Do not recreate repaired math from Markdown.

From the repository root, with python-docx1.2.0,lxml6.1.1,Matplotlib3.10.8 and NumPy2.3.5:

```bash
python paper/eex_final_v10_20261011/tools/build_price_figure.py --source paper/eex_price_integrated_v9_20261011 --out paper/eex_final_v10_20261011
python paper/eex_final_v10_20261011/tools/build_v10.py --source paper/eex_price_integrated_v9_20261011 --out paper/eex_final_v10_20261011
```

The figure script reads frozen summary values only. The document builder verifies three source hashes, preserves original mathematical text and all numerical table cells, then applies REVISION_PLAN.json. No old model, notebook, pickle or price-estimation code is executed.

The PDFs are renderings for manuscript review and SI delivery. Font availability and office-renderer versions can affect pagination; the checked local rendering is21 main+14SI+1title pages. Microsoft Word/WPS native execution has not been tested.

support/FINAL_QA.json records local final checks; a separate PUBLICATION_RECEIPT.json records actual remote delivery when present. support/BUILD_QA.json is generated during a build and can have visual_review=pending even when the later FINAL_QA reports completed visual inspection. These records have different scopes and timestamps.

DATA_AND_CODE_ACCESS.md gives statistical reproduction boundaries. tables/PRICE_DISPLAY_LEDGER_V10.csv maps156 frozen public values to current table/figure locations; it is not a private-row replication. The previous support/AGGREGATE_AUDIT.json is retained as a historical review receipt, not claimed as rerun in this editorial pass.
