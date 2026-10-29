# 0.3.1 production verification — maintainer report

**Result: PASS — LIVE_VERIFIED (maintainer-reported), 2026-10-29.** The maintainer reported a successful production upgrade from `0.1.0` to `0.3.1` and a real HTML newsletter import with visual PDF inspection. This is a report from one production installation, separate from the reproducible [synthetic CI tests](integration-report-0.3.1.md). The repository agent did not independently inspect the production system or private message.

## Reported environment and installation

| Component | Reported value |
| --- | --- |
| Paperless-ngx | `3.3.0` |
| Installation | Native installation in a Proxmox LXC; no Docker |
| Python | `3.13.14` |
| Plugin upgrade | `0.1.0` → `0.3.1`, installed with `uv pip install --no-deps` |
| Header language | `PAPERLESS_MAIL_HEADER_LANGUAGE=de` |
| Paperless time zone | `PAPERLESS_TIME_ZONE=Europe/Berlin` |
| Gotenberg | `8.34.0`; external images allowed, JavaScript disabled, private IPs blocked |

The official release wheel was verified against SHA-256 `4de51242454b5d90b17cc3ae05f83ffd00439bfb5a78968ae19023d1d95d3dcc`. The maintainer reported no changes to Paperless or its dependencies, successful restarts of the consumer, task worker and webserver, and a saved rollback wheel and original configuration.

## Confirmed production scope

The maintainer's checks inside the Paperless Django environment reported the `Paperless-ngx Mail Header` parser at version `0.3.1`, language `de` and effective time zone `Europe/Berlin`. The production log identified that parser for the imported message and reported successful completion.

Visual inspection of the generated PDF confirmed:

- German `Von`, `An`, `Datum`, `Betreff` labels and the expected German date format and Berlin-local time.
- Correct addresses and subject, including Unicode and emoji in the subject.
- Retained HTML text formatting, colors and layout.
- Visible external images, including logos and product images, under the reported Gotenberg policy.
- Successful PDF creation, thumbnail generation and document import.

The maintainer confirmed that the previous German header appearance was retained during the upgrade. External-image loading remains controlled by Gotenberg; this result is not a recommendation to change its policy. See [privacy and security](privacy-security.md).

## Observations and limits

The maintainer observed Granian ASGI transport-close messages during processing, but the document import completed successfully. No causal connection to the plugin has been established. An unsuitable correspondent/document-type assignment was also observed in downstream automatic classification; it is not established as a plugin defect. Neither observation prompted a plugin-code change.

This production test covers one real HTML newsletter on the exact environment above. It does **not** establish production verification of separate PDF attachment imports, IMAP/mail-rule attachment extraction, plain-text-only or CID messages, OCR/PDF/A behavior, English/other locales, other time zones, UTC fallback, DST transitions or other Paperless versions. Some of those paths have separate synthetic CI evidence; that evidence must not be presented as a production observation. No production original-file byte comparison was reported.

No real email, PDF, screenshot, address, document ID, container ID, host/IP or raw production log is published with this report. The [v0.3.1 release](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/releases/tag/v0.3.1), its tag and its assets remain unchanged.
