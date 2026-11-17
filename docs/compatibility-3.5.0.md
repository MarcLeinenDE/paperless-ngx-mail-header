# Paperless 3.5.0 compatibility — v0.3.2 candidate

Status: **source-reviewed, not yet real-stack verified**. This page is a test plan, not a completed release report.

## Confirmed upstream behavior

- On Paperless-ngx 3.3.0, `MailDocumentParser.generate_pdf_from_html(orig_html, attachments)` takes two positional arguments.
- On Paperless-ngx 3.5.0, the native HTML converter additionally accepts a keyword-only `convert_to_pdfa=True`. Its `generate_pdf` passes `convert_to_pdfa=False` for HTML, applying PDF/A at the final merge instead of an intermediate conversion.
- The `paperless_ngx.parsers` entry point remains unchanged between those two tags.

Source: https://github.com/paperless-ngx/paperless-ngx/blob/v3.5.0/src/paperless/parsers/mail.py and https://github.com/paperless-ngx/paperless-ngx/blob/v3.3.0/src/paperless/parsers/mail.py

## Compatibility strategy

The 0.3.2 candidate accepts and forwards `**kwargs` on its `generate_pdf_from_html` override. It does **not** set `convert_to_pdfa` itself, so Paperless 3.3.0 sees its original call and Paperless 3.5.0 receives its requested flag. All other email conversion and final PDF/A work stays native.

## Release verification required

- Offline tests must simulate 3.3.0 and 3.5.0 native signatures and verify the 3.5.0 PDF/A flag is forwarded as `False` (and the default `True` when directly invoked).
- The same wheel must pass real-stack English/German language and Berlin/New York/UTC time-zone scenarios for **both** Paperless versions.
- Check native text-only delegation, HTML header insertion, CID resources, original bytes and native searchable content parity. Review PDF evidence for layout and PDF/A as configured.
- Keep Gotenberg/Tika versions and their test scope explicit; IMAP mail-rule retrieval and actual production deployment remain untested.
- Only after all checks pass may this candidate be represented as compatible in a published release.
