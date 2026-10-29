# 0.3.1 production verification

**Result: PASS — LIVE_VERIFIED (operator-reported), 2026-10-29.** The published `0.3.1` release was reported to process one real HTML newsletter successfully, with visual PDF inspection. This observation comes from one installation and is separate from the reproducible [synthetic CI tests](integration-report-0.3.1.md).

## Compatibility scope

| Component | Tested value |
| --- | --- |
| Paperless-ngx | `3.3.0` |
| Plugin | `0.3.1` |
| PDF renderer | Gotenberg `8.34.0` |
| Header language | German (`de`) |
| Time zone | `Europe/Berlin` |

## Confirmed behavior

The operator reported successful parser selection at version `0.3.1`, document consumption and visual confirmation of:

- German `Von`, `An`, `Datum`, `Betreff` labels and the expected German date format and Berlin-local time.
- Correct address and subject rendering, including Unicode and emoji.
- Preserved HTML text formatting, colors and layout.
- Visible external images under the configured Gotenberg policy.
- Successful PDF creation, thumbnail generation and document import.

External-image loading is controlled by Gotenberg; see [privacy and security](privacy-security.md). No real message, screenshot or raw production log is included in this report.

## Limits

The report documents operator-provided observations, not an independent production inspection by the repository agent. It does not establish production verification of separate PDF attachment imports, IMAP/mail-rule attachment extraction, plain-text-only or CID messages, OCR/PDF/A behavior, other languages or time zones, UTC fallback, DST transitions or other Paperless versions. Original-file byte comparison was not part of this production check.

Some of those paths have separate [synthetic CI evidence](integration-report-0.3.1.md); that evidence does not extend the production scope above.
