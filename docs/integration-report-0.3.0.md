# Real-stack i18n evidence for 0.3.0

The first successful [English/German integration run](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/actions/runs/40883834734) used the same built wheel in two language jobs. Each job started an independent native baseline and plugin-enabled Paperless `3.3.0` instance with Python `3.14.8`, Gotenberg `8.37` and Tika image `3.3.1.0`.

| Language job | Service setting | Result |
| --- | --- | --- |
| English | `PAPERLESS_MAIL_HEADER_LANGUAGE` absent | PASS: From, To, Date, Subject; `2026-10-29, 10:15` |
| German | `PAPERLESS_MAIL_HEADER_LANGUAGE=de` | PASS: Von, An, Datum, Betreff; `29.10.2026, 10:15 Uhr` |

Both jobs produced 13 valid documents per native/plugin instance and identically rejected an email without the mandatory sender. Original files and searchable text matched the native baseline. Plain-text-only and separately uploaded PDF output stayed on the native path. CID/controlled HTTP images, escaped Unicode fields, missing optional headers, mixed line separators and both DST transitions passed in both languages.

All 13 English candidate PDF pages were visually inspected. Every German candidate PNG was byte-identical to the corresponding visually reviewed `0.2.0` output. This verifies German label/date/layout compatibility for the synthetic matrix, not every possible email layout.

The first tested workflow merge commit was `d1129e133ae0fc0c7ca79db63758586ea18b326e`; its shared wheel SHA-256 was:

```text
5ed3863932bbebdcd8b5814fa8972f8c74ce43d65a5eb73ab6793da1f1a82857
```

That hash identifies the first passing candidate. Before publication the final merged commit runs the same matrix again. Release `integration-summary.json` records the final commit, workflow, selected languages and exact shared wheel hash; the synthetic evidence archive preserves PDF/PNG output for each language.

## Catalog contribution checks

58 offline tests pass locally and in the Python 3.12–3.14 CI matrix. These cover English defaults, explicit German selection, regional aliases, invalid/corrupt-catalog fallback, escaped translated labels, catalog-only language discovery and RTL layout structure using temporary test catalogs.

The documented `pybabel init` → translation → compilation → validation process was additionally exercised with a temporary French catalog in a disposable copy. French is not shipped in this release. The project discovers `.mo` catalogs automatically, checks their `.po` sources and derives its integration language matrix from the same installed package. Translation contributors do not edit a language registry or CI workflow.

## Scope and limits

All data and credentials were synthetic and disposable. No production instance was accessed. The PDF attachment was uploaded separately; external IMAP fetching and mail-rule attachment extraction were not exercised. Actual translated output was integrated and visually reviewed for English/German only. RTL behavior has structural unit coverage; a future RTL or non-Latin catalog still requires real PDF/font review by its contributor.

Europe/Berlin remains independent of language. Generated PDFs retain their import-time language. See [configuration](configuration.md#header-language) and [the translation guide](translations.md).
