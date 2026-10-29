# Real-stack integration evidence for 0.2.0

The first complete [successful integration run](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/actions/runs/40870954321) finished on 2026-10-29. All input was generated synthetic data in disposable GitHub Actions containers; the maintainer's production environment was not accessed.

## Environment

| Component | Version / configuration |
| --- | --- |
| Paperless-ngx | `3.3.0`, official image; independent native and plugin instances |
| Python inside Paperless | `3.14.8` |
| Candidate plugin | `0.2.0`, installed from the built wheel using `uv pip install --system --no-deps` |
| Native parser | `Paperless-ngx Mail Parser` `3.3.0` |
| Selected candidate parser | `Paperless-ngx Mail Header` `0.2.0` |
| Gotenberg | `8.37`; JavaScript disabled, controlled image server explicitly allowed |
| Tika | image `3.3.1.0` |
| Database / broker | Separate SQLite databases and Valkey database indexes |

## Results

Each instance received 14 synthetic uploads: 13 valid documents and one email without the mandatory `From` header. Both produced exactly 13 documents and rejected the invalid message with `Missing 'from'`.

| Case | Result |
| --- | --- |
| HTML-only email | PASS: four localized rows above the original body |
| Plain-text-only email | PASS: PDF text and page count match the native baseline |
| Inline CID image | PASS: image present in native and candidate PDFs |
| Controlled external HTTP image | PASS: image present under the explicit Gotenberg policy |
| HTML with PDF attachment | PASS: EML bytes preserved and HTML body rendered |
| Separate PDF attachment upload | PASS: original PDF preserved; native and candidate PDF text/page count match |
| Unicode and escaping | PASS: umlauts, ampersand, angle brackets and quoted subject rendered as text |
| Mixed line separators | PASS: header precedes body, no tag corruption |
| Missing optional recipient/subject | PASS: valid email renders with missing-value markers |
| Missing mandatory sender | PASS: identical native validation rejection |
| Spring DST boundary, before/after | PASS: Berlin times `01:59` and `03:00` |
| Autumn DST boundary, before/after | PASS: Berlin times `02:59` and `02:00` |

For every accepted file, the downloaded original matched the input byte-for-byte, and searchable text matched between the native and plugin stacks. All generated PDFs contained the expected body text. Candidate HTML PDFs contained exactly one instance of each label and the correct Berlin timestamp. Image-bearing PDFs contained images. All 13 one-page candidate PDFs were visually inspected for header position, legibility, escaping and image rendering.

## Artifact binding

The first successful run tested workflow merge commit `30c2010ccc235e16ddcf4d015c98c71da98d12b0` and wheel SHA-256:

```text
255a9def0d6f937b9d3590789828c5044fa3f8710568c80a5a468d4bb35f7774
```

This identifies the first passing candidate, not necessarily the final release asset after documentation changes. Before publication, the final merged commit runs the same integration workflow again. Its `integration-release` artifact provides the exact tested wheel/source files; `integration-summary.json` on the GitHub release records that final wheel hash and workflow run. `SHA256SUMS.txt` binds all release assets. Synthetic PDF/PNG evidence is included in the release evidence archive.

## Limits

This verifies real REST upload, Celery consumption, parser selection, Tika indexing and Gotenberg conversion. The attachment PDF was uploaded separately: external IMAP fetching and mail-rule attachment extraction were not exercised. There was no test of other Paperless releases, every possible HTML layout, or the maintainer's production deployment. Other 3.x versions remain unverified even where parser source matches.

All containers and their volumes were removed by the workflow. No private email, personal screenshot or production credentials were used.
