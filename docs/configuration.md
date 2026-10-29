# Configuration and mail rules

This extension deliberately has **no runtime configuration file**, no environment variable, and no new Paperless mail rule. The native parser controls ingestion exactly as before.

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
