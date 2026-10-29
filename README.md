# Paperless-ngx Mail Header

A lightweight, unofficial **Paperless-ngx 3** parser extension that adds an email's **sender, recipient, date and subject** above its existing HTML content in the generated PDF. Everything else stays with Paperless-ngx's native mail parser.

> [!IMPORTANT]
> This is an independent community extension, **not affiliated with, endorsed by, or officially supported by Paperless-ngx**. Version `0.2.0` is the initial public repository version; a stable release has not yet been tagged. Its formatter is byte-identical to the maintainer's production `0.1.0`; parser changes are limited to version, author and project URL. The new package itself has not been deployed to that production environment.

![Anonymized example of the PDF email header](docs/images/mail-header-example.png)

*Illustration generated from the actual header formatter with fictional addresses. It is not a screenshot of a personal email.*

## Features

- Inserts four localized rows: **Von**, **An**, **Datum** and **Betreff**.
- Shows the email's timestamp in **Europe/Berlin**, including daylight-saving time.
- Escapes header values before inserting HTML.
- Preserves the original HTML body without re-serializing it; native Paperless continues to render via Gotenberg.
- Leaves plain-text-only messages on the existing Paperless text-rendering path (which already includes mail headers).
- Leaves the original `.eml`, attachment filtering, OCR, PDF/A, Gotenberg handling, indexing and workflows unchanged.
- Uses the documented Paperless parser entry point, rather than modifying Paperless application files.

## Status and compatibility

| Component | State | Evidence |
| --- | --- | --- |
| Paperless-ngx `3.3.0` | **Live verified for HTML header** | Installed local `0.1.0` plugin; PDF screenshot confirms header rendering |
| Paperless-ngx other 3.x releases | **Not verified** | Parser internals can change between versions |
| Unit test suite | **Unit tested** | 22 tests pass locally on Python 3.12; tests use a native-parser test double, not an integrated Paperless stack |
| Plain-text-only `.eml` | **Native fallback** | Verified by unit tests; integrated visual rendering not separately confirmed |
| HTML with PDF attachments | **Native delegation** | Unit-level check; production import semantics are controlled by Paperless rules |

Repository version: `0.2.0`. See [the source comparison](docs/source-comparison.md) for the evidence connecting it to the production `0.1.0` package. A stable release tag remains subject to the integration checklist.

## Installation

Install the **built wheel** in the *same Python environment* used by Paperless and restart the processes that load the parser registry. **Do not modify mail rules just to activate the plugin.** See:

- [Installation — LXC / community-scripts and Docker](docs/installation.md)
- [Configuration and HTML layout](docs/configuration.md)
- [Troubleshooting and rollback](docs/troubleshooting.md)

For a known community-scripts LXC layout, the package is installed in `/opt/paperless/.venv`; the reference instructions use `uv pip install --python ... --no-deps`.

## Quick check

After installing in the correct Python environment, Paperless should log something like:

```text
Loaded third-party parser 'Paperless-ngx Mail Header' ...
Document handled by third-party parser 'Paperless-ngx Mail Header' ...
```

The plugin handles only `message/rfc822`; it does not replace PDF, raster-image or office-document parsers.

## Development

```bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m pip install build
python -m build
```

Tests use test doubles instead of a live Paperless installation. A real end-to-end test with Paperless/Gotenberg/Tika is required before publishing a stable release; see [Testing](docs/testing.md).

## Project layout

```text
src/paperless_ngx_mail_header/   Plugin entry point and isolated HTML formatter
tests/                           Offline regression tests
docs/                            Installation, configuration, privacy and compatibility
scripts/                         Deterministic anonymized example-image generator
.github/workflows/               Offline test and package-build CI
AGENTS.md                         Coding-agent constraints and release gates
CODEX_HANDOFF.md                  Requested work and acceptance criteria
```

## Privacy and security

The extension does not independently call remote services. By default, Paperless itself may call Gotenberg or Tika according to its configuration. Loading remote images is controlled **separately by Gotenberg**; enabling that feature can fetch tracking pixels or attacker-controlled URLs. See [Privacy and security](docs/privacy-security.md).

Never commit real `.eml` messages, document scans, invoices, customer IDs or live mail addresses as test samples. The example image uses fictional values.

## Contributing

Contributions are welcome under the project's documented license policy. Keep the plugin intentionally small, write regression tests, and distinguish *unit tested* from *live verified*. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).

## Licensing

- **Project-authored software:** GNU GPL-3.0-or-later (see [LICENSE](LICENSE)).
- **Project-authored documentation and example image:** CC BY-SA 4.0 (see [LICENSES.md](LICENSES.md) and [the canonical license text](https://creativecommons.org/licenses/by-sa/4.0/legalcode)).
- Third-party programs and dependencies keep their own copyright and licenses. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Disclaimer and no warranty

Provided **AS IS**, without warranty. This plugin depends on Paperless internals and may need updates for future releases. It does not replace secure email handling or document-integrity controls. Product names and trademarks belong to their respective owners.

---

### ☕ Like this project?

If this project helped you, [buy me a coffee via PayPal](https://www.paypal.me/ccaa/) if you wish. No obligation — a ⭐, useful issue, or contribution is equally appreciated. See [SUPPORT.md](SUPPORT.md).
