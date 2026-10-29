# Contributing

Thank you for improving this independent Paperless-ngx extension. Please keep changes narrow and evidence-backed.

1. Read [AGENTS.md](AGENTS.md), [docs/testing.md](docs/testing.md), and the relevant source file.
2. Prefer upstream `MailDocumentParser` behavior and override only what the header requires.
3. Add offline tests for changed behavior, including representative HTML input, escaping and text-only fallback.
4. Do not change attachment imports, OCR, Tika, Gotenberg, PDF/A or mail rules without a separately reviewed scope change.
5. Distinguish unit-tested behavior from actual end-to-end validation against a named Paperless version.
6. Never submit real emails, documents or personal identifiers to tests or issue reports.
7. Apply the license policy in [LICENSES.md](LICENSES.md) to contributions you have the right to license.

PRs are welcome. This is a personal spare-time community project with no response-time commitment.
