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

## Evidence classes

- `LIVE_VERIFIED`: Observed through real Paperless and rendered PDF, with exact version/date recorded.
- `UNIT_TESTED`: Offline tests using mocks/stubs only.
- `NOT_VERIFIED`: Pending test or unknown compatibility.
- `KNOWN_ISSUE`: Reproducible failure with an issue and expected mitigation.

As of 2026-10-29, the working local `0.1.0` plugin is `LIVE_VERIFIED` for the HTML four-row header on Paperless-ngx `3.3.0` based on the maintainer's report recorded in the handoff. The new `0.2.0` packaging itself is **not** live deployed. Its runtime source matches `0.1.0` after excluding project metadata; see [the source comparison](source-comparison.md).

## Release gate

A stable release requires an authorized environment, real integration smoke test, exact version report, offline tests on configured Python versions, package build and import/entrypoint check, license review, and explicit user permission to publish.
