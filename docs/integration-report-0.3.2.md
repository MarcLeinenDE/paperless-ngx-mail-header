# 0.3.2 compatibility validation

Plugin 0.3.2 forwards the native HTML converter's keyword arguments unchanged. Paperless 3.5.0 passes `convert_to_pdfa=False` and applies PDF/A when merging the final archive; Paperless 3.3.0 supplies no new keyword. The plugin adds no PDF/A implementation or runtime dependencies. See the [upstream interface review](compatibility-3.5.0.md).

## Completed PR validation, 2026-11-17

[PR #15](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/pull/15), source head `37526556158b4daf991cb6e1009582dc4291e386`, was tested by GitHub on its synthetic merge commit `4de3174e2b473bd7563e0fd4149323497735a588`:

- [Unit/package run 44135474143](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/actions/runs/44135474143): **140 tests passed on each of Python 3.12, 3.13 and 3.14**, translation validation, wheel/sdist content checks and strict Twine metadata checks passed.
- [Real-stack run 44135474904](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/actions/runs/44135474904): **all eight scenarios passed** using one wheel, SHA-256 `10a390592a5de4b369084b12ac86d805f7550595e710716591111e37c3d3b61e`. This hash identifies the PR candidate, not a separately rebuilt final-main release asset.
- CodeQL's Actions and Python analyses passed. The complete PR diff was reviewed; the native interface was compared against both upstream tags.

| Paperless | Language | Effective time zone | Result |
| --- | --- | --- | --- |
| 3.3.0 | English, language unset | Europe/Berlin | PASS |
| 3.3.0 | German | Europe/Berlin | PASS |
| 3.3.0 | English, language unset | America/New_York | PASS |
| 3.3.0 | English, language unset | UTC, variable absent | PASS |
| 3.5.0 | English, language unset | Europe/Berlin | PASS |
| 3.5.0 | German | Europe/Berlin | PASS |
| 3.5.0 | English, language unset | America/New_York | PASS |
| 3.5.0 | English, language unset | UTC, variable absent | PASS |

Each scenario used disposable native and plugin stacks with Gotenberg 8.37 and Tika image 3.3.1.0. Observed Paperless versions and actual Django time-zone settings matched in both stacks. Every stack imported 13 valid synthetic documents and rejected the mandatory-From-negative case: **208 successful documents and 16 expected rejections** across the matrix.

Original bytes and native searchable text matched. Text-only and separately uploaded PDF attachments retained native PDF text/page counts. HTML headers appeared once, above the body, with correct localized timestamps including DST boundaries. CID/controlled external images, Unicode/escaping, optional missing fields and mixed line separators passed. All 208 PDF hashes were independently compared with the scenario summaries; native/plugin PNG comparisons showed readable headers, preserved content and no clipping or overlap.

## PDF/A processing and limits

All 208 downloaded PDFs declared **PDF/A-2B** in XMP. The upstream final-conversion path and native OCRmyPDF success logs were inspected. This verifies the observed processing and metadata; an independent veraPDF conformance certification was **not** performed. Native and plugin logs include nonfatal Ghostscript complex-script/ToUnicode warnings and Tesseract diagnostics for the separately uploaded PDF fixture; both completed PDF/A output and preserved the tested searchable content. These results do not establish complex-script OCR quality.

All inputs are synthetic. REST upload, real Celery consumption, registry selection, Tika indexing and Gotenberg rendering were exercised. IMAP fetching, mail-rule attachment extraction, other Paperless versions and production deployment were not tested. The [0.3.1 operator report](production-report-0.3.1.md) remains a distinct, narrower observation.

## Final-main release evidence

The [release checklist](release-checklist.md) requires the latest PR head to pass before merge, then repeats the full unit/package and eight-scenario integration matrix on the final main commit. The authoritative [v0.3.2 GitHub Release](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/releases/tag/v0.3.2) publishes the final commit/run IDs, aggregate `integration-summary.json`, synthetic PDF/PNG evidence archive, wheel, sdist and `SHA256SUMS.txt`. Verify every scenario's final-commit and shared-wheel binding against those assets. The completed PR run above is not a substitute for that final-main gate.

English remains the default; select German with `PAPERLESS_MAIL_HEADER_LANGUAGE=de`. Header time follows Paperless `PAPERLESS_TIME_ZONE`, with UTC when unset; use `Europe/Berlin` to preserve the pre-0.3.1 time basis. Existing PDFs and production installations are not changed by publication.
