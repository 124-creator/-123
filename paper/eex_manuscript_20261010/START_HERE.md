# EEX manuscript v2: journal-oriented revision

Date: 2026-10-10. Working target: **Empirical Economics**. Status: **REVISED_AUTHOR_REVIEW_DRAFT**, not submission-ready and not a confirmed CAS-zone-3 journal match.

Start with [MANUSCRIPT_EN.md](MANUSCRIPT_EN.md), then [SUPPLEMENT_EN.md](SUPPLEMENT_EN.md). [TARGET_JOURNAL_REVIEW_ZH.md](TARGET_JOURNAL_REVIEW_ZH.md) records actual journal/paper reading and the fit decision; [REVISION_NOTES_ZH.md](REVISION_NOTES_ZH.md) explains the substantive changes. The downloadable author package additionally contains `REVISION.diff`, the full line-by-line comparison with the previously delivered v1.

The revision prioritizes the economic question and temporal heterogeneity; it removes duplicate A/B presentation, consolidates repeated caveats, and separates reported-indicator association from latent or causal interpretations. No statistical result was changed or newly estimated.

Human authors must complete [TITLE_PAGE_AND_DECLARATIONS.md](TITLE_PAGE_AND_DECLARATIONS.md). [COVER_LETTER_DRAFT_EN.md](COVER_LETTER_DRAFT_EN.md) is unsent and needs their approval. Source access and failures are in [SOURCE_LEDGER_V2.json](SOURCE_LEDGER_V2.json).

## Editable document and figures

The downloadable author package contains the Word manuscript. Repository sources reproduce it:

```bash
python tools/build_figures.py
python tools/build_docx.py
```

Run from this directory. Python dependencies: matplotlib, python-docx, lxml; Pandoc must be installed. The script produces MANUSCRIPT_EN.docx and does not fit a model. The repository includes SVG figures and their exact saved estimates; the script also generates EPS and PNG. The downloadable author package contains the rendered Word, EPS/PNG figures, frozen-output copies and detailed validation. Word uses PNGs rendered from the same data. Numeric provenance and scoped manuscript QA are under tables/ and support/.

## Frozen evidence

Input: `5745eb3ddca79602346053446583d794b0e09800`.
Principal analysis: `e25c1e02e1a58e0aec1084f7419066855e9565ec`.
Robustness: `d4b26f1bbd8c1d7c036259e48e119c9c12f6c9a9`.

The prior v1 manuscript was delivered in chat but not pushed. This directory is a new publication of the revised source; it does not overwrite a remote v1, raw data or experiment. No journal submission, new email, new model training or full-repository PASS is claimed.
