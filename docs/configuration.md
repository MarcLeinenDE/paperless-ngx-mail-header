# Configuration and mail rules

The native parser controls ingestion and mail rules as before. Starting with `0.3.0`, one plugin environment variable selects the language of the inserted HTML header.

## Header language

`PAPERLESS_MAIL_HEADER_LANGUAGE` defaults to `en`. The available initial languages are:

| Value | Header labels | Example date |
| --- | --- | --- |
| `en` or unset | From, To, Date, Subject | `2026-10-29, 10:15` |
| `de` | Von, An, Datum, Betreff | `29.10.2026, 10:15 Uhr` |

**Upgrading from 0.2.0:** set `PAPERLESS_MAIL_HEADER_LANGUAGE=de` to retain German labels and the previous date format. English is now the default. Both languages keep the existing Europe/Berlin time zone, including DST. The plugin does not change the Paperless server's global time zone.

For Docker Compose, add the setting to the existing Paperless service environment (and separate worker services if used):

```yaml
environment:
  PAPERLESS_MAIL_HEADER_LANGUAGE: de
```

For LXC or another service-based installation, supply `PAPERLESS_MAIL_HEADER_LANGUAGE=de` through the environment configuration of the actual Paperless consumer, workers and webserver. Restart those processes after changing it. Exporting the variable in an unrelated terminal does not change an already-running service.

This is an installation-wide PDF output setting. The language of the browser interface, OCR and the original email does not select it automatically. A generated PDF keeps its language until explicitly regenerated; shared documents do not change language for each viewer.

Codes are case-insensitive; `_` and `-` are accepted as region separators. `de-DE` falls back to the shipped `de` catalog. An unsupported or unreadable catalog falls back to English with a warning, so a language configuration error does not block email processing.

Additional languages can be contributed as gettext catalogs through a PR; see [the translation guide](translations.md). No new runtime dependency or Paperless source modification is required.

## HTML-only mail rule

Existing Paperless rules using **HTML only** generate an HTML PDF; the plugin inserts a header above the HTML body when a renderable HTML part exists. The original page styles and CID-handling path remain upstream. The plugin does not change `MailRule.PdfLayout` values.

## Plain-text-only mail

If the message has no HTML part, native Paperless generates its text representation with From, To, Subject, Date and other applicable headers. This extension leaves that behavior unmodified, so the gray four-row HTML header is not applied to text-only messages.

## Attachments

Separate attachment extraction is managed by Paperless's mail rule consumption scope and attachment filters. This plugin neither merges attachments nor creates separate documents. Email + attachment handling should be tested against the current native parser after every update.

## Rendering notes

- HTML content is **inserted into**, not rewritten as, a new DOM document by the plugin.
- Remote images may be disabled by default in Gotenberg. See [privacy and security](privacy-security.md) before changing this.
- Because the header adds vertical space, page breaks can differ from unmodified Paperless output.
- Existing PDF archives are not retroactively updated.
