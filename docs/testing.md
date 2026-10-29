# Testing and evidence

## Offline tests

```bash
python -m pip install -e '.[test]'
python -m pytest -q
```

The offline suite uses pure formatter tests plus a test double for the native Paperless `MailDocumentParser`. This validates narrow method delegation, **not** full Gotenberg/Tika/Paperless integration.

## Minimum integration matrix

| Input | Expected behavior | Verification |
| --- | --- | --- |
| HTML email without attachment | Four-row header above HTML body | Rendered PDF screenshot, selected parser log |
| Text-only email | Native email header and text | Rendered PDF comparison |
| HTML with inline CID image | Native resource handling | Image visible in PDF |
| HTML with external HTTPS image | Gotenberg policy determines fetch | Image visible, compare logs |
| HTML + PDF attachment | Mail rule handles attachment separately | Expected number of documents, attachments byte comparison |
| German text and escaped characters | No leaked markup or missing characters | Extracted PDF text and visual inspection |
| Summer/winter time | Correct Berlin-local timestamp | Metadata check and PDF view |
| EML without expected fields | No crash, reasonable missing-value display | Test fixture |

## Disposable real-stack integration

The `Real Paperless integration` GitHub Actions workflow starts fresh native and plugin-enabled Paperless `3.3.0` containers with Gotenberg `8.37` and Tika `3.3.1.0`. It builds and installs the actual candidate wheel with `--no-deps`. REST uploads are processed by real Celery workers and the real parser registry; generated PDFs and searchable text are compared with the native baseline.

The synthetic cases cover HTML, plain text, CID and controlled external images, HTML with a PDF attachment, Unicode/escaping, mixed line separators, missing header fields and both DST transitions. The PDF attachment is also uploaded as a separate document. The test compares document counts, unchanged original bytes, PDF text, image presence and registry selection. The controlled image server is internal to this disposable network; no real mail is sent or fetched.

The native parser requires a `From` header. Missing recipient and subject values are tested on valid messages; a separate message without `From` must be rejected identically by both stacks. The plugin does not relax native message validation.

External IMAP fetching and mail-rule attachment extraction are outside this integration scope. Evidence artifacts contain synthetic PDFs, first-page PNGs, exact versions, the candidate commit and wheel SHA-256. The workflow always removes its containers and volumes afterward. These are real-stack synthetic tests, not evidence from the maintainer's production environment.

## Evidence classes

- `LIVE_VERIFIED`: Observed through real Paperless and rendered PDF, with exact version/date recorded.
- `UNIT_TESTED`: Offline tests using mocks/stubs only.
- `NOT_VERIFIED`: Pending test or unknown compatibility.
- `KNOWN_ISSUE`: Reproducible failure with an issue and expected mitigation.

As of 2026-10-29, the working local `0.1.0` plugin is `LIVE_VERIFIED` for the HTML four-row header on Paperless-ngx `3.3.0` based on the maintainer's report recorded in the handoff. The new `0.2.0` packaging itself is **not** live deployed. The initial import matched `0.1.0` after excluding project metadata; two later formatter edge-case corrections have regression tests; see [the source comparison](source-comparison.md).

## Release gate

A stable release requires an authorized environment, real integration smoke test, exact version report, offline tests on configured Python versions, package build and import/entrypoint check, license review, and explicit user permission to publish.
