# Production source comparison and release changes

The initial import was compared on 2026-10-29 with the wheel from the maintainer-supplied private `0.1.0` ZIP. The table and byte hashes below describe that initial import before the subsequent release-readiness fixes recorded at the end of this document.

The maintainer selected `0.2.0` as the first public repository version provided that its runtime code matches production. The comparison confirms that condition.

| Source file | Difference from production `0.1.0` |
| --- | --- |
| `formatting.py` | Byte-identical |
| `parser.py` | Only the class metadata `version`, `author` and `url` changed |
| `__init__.py` | Only the module docstring and `__version__` changed |

At the initial import, all three Python files had identical abstract syntax trees after normalizing only those metadata assignments and the package docstring. The complete textual diff was also checked. At that point no formatter, scoring, method signature, delegation or cleanup logic had changed.

The production wheel and the prepared package advertise the same single parser entry point:

```ini
[paperless_ngx.parsers]
paperless_mail_header = paperless_ngx_mail_header.parser:MailHeaderParser
```

SHA-256 of the supplied production wheel:

```text
06c852b2fb78c720bbbc241989d2dd537d67d3b98c5bdf9a5c3cd6d272946f98
```

SHA-256 of `formatting.py` in production `0.1.0` and the initial import (before release-readiness fixes):

```text
097b41dfb0f72e838c1621c316a3e21a3b568f17c68b4b3259628a20fdf852b7
```

## Packaging and documentation changes

- Package, parser and module versions are `0.2.0`.
- Public author and project URL replace generic local metadata.
- The prepared handoff replaces the originally generated MIT notice with GPL-3.0-or-later for project software and CC BY-SA 4.0 for project documentation and examples. The maintainer identified the original license choice as a mistake.
- README, installation and testing documentation, synthetic example, and CI configuration are included in the repository preparation.
- The build requirement is setuptools 77 or newer for the SPDX license string already used in `pyproject.toml`.

## Validation and limits

- All 22 existing offline tests pass with Python 3.12.14.
- Both the source distribution and a wheel built from that distribution build successfully.
- This is a source comparison and offline package check, not a new integration test. The tests replace Paperless with a native-parser test double.
- The maintainer's production report concerns the HTML header in `0.1.0` on Paperless-ngx `3.3.0`. `0.2.0` itself has not been deployed there.
- Python 3.13/3.14 and the full integration matrix have not been independently executed during this local comparison. The upstream hooks were subsequently inspected as recorded below.
- The maintainer authorized the repository and initial import after reviewing this comparison. No production changes or public release tag are part of the import.

## Upstream source inspection

Before the repository import, the hooks were compared with [Paperless-ngx v3.3.0 `mail.py`](https://github.com/paperless-ngx/paperless-ngx/blob/v3.3.0/src/paperless/parsers/mail.py) (Git blob `198a2b544b811137532f5256657741cee2f8bbd7`). The `score`, `generate_pdf` and `generate_pdf_from_html` parameter contracts match; the native score is 10. The native implementation handles text-only fallback, layout selection, CID resources and conversion. This was source inspection, not execution of the real Paperless stack.


## Subsequent release-readiness changes

The final candidate intentionally differs from the initial import in two formatter edge cases discovered by additional tests:

1. HTML line offsets now follow only LF, matching `HTMLParser.getpos()`. Previously a standalone CR, form feed or Unicode line separator followed by LF could place the inserted header inside a tag. Existing input text is still preserved exactly apart from inserting the header.
2. A date that overflows Python's supported range when converted to Europe/Berlin is displayed as `—` rather than failing the conversion.

These are the only runtime logic changes. `parser.py` still differs from production only in project metadata, and native attachment, plain-text and PDF handling remain delegated upstream. The old byte-identical formatter claim does **not** apply to this final candidate.

Final candidate `formatting.py` SHA-256:

```text
2cd93de7a94c3c28d789241973f9c7e9099b472bcbfe5abc8539fcd7516c1540
```

The expanded offline suite contains 40 cases, including actual `imap-tools` RFC822 decoding, charset handling, DST boundaries and the two regression cases. It passes locally with Python 3.12.14. A subsequent real Paperless/Gotenberg/Tika integration run passed; see [integration-report.md](integration-report.md) for exact versions, scope and artifact binding.

Paperless-ngx `v3.3.4`, the latest release checked on 2026-10-29, has the same native `mail.py` Git blob (`198a2b544b811137532f5256657741cee2f8bbd7`) as `v3.3.0`. Source identity is not a live compatibility claim for `3.3.4`.
