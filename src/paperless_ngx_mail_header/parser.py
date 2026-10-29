"""Paperless-ngx 3 hook: only supplement the native HTML e-mail PDF view.

No custom MIME parsing, attachment conversion, OCR, PDF/A, thumbnail generation
or changes to the e-mail rule settings.
"""

from __future__ import annotations

import os

from paperless.parsers.mail import MailDocumentParser as NativeMailDocumentParser

from .formatting import add_header_to_html, render_header
from .i18n import LANGUAGE_ENV


class MailHeaderParser(NativeMailDocumentParser):
    name = "Paperless-ngx Mail Header"
    version = "0.3.0"
    author = "Marc Leinen"
    url = "https://github.com/MarcLeinenDE/paperless-ngx-mail-header"

    @classmethod
    def score(cls, mime_type: str, filename: str, path=None) -> int | None:
        # Match *only* .eml; no competition with PDF, images, OCR or office parsers.
        if mime_type != "message/rfc822":
            return None
        return 20  # Native mail parser has score 10 in Paperless-ngx 3.

    def generate_pdf(self, mail_message, pdf_layout=None):
        # Pass the message to just the HTML generator; delegate everything else.
        self._header_mail_message = mail_message
        try:
            return super().generate_pdf(mail_message, pdf_layout)
        finally:
            self._header_mail_message = None

    def generate_pdf_from_html(self, orig_html, attachments):
        message = getattr(self, "_header_mail_message", None)
        if message is not None:
            header = render_header(message, language=os.environ.get(LANGUAGE_ENV, "en"))
            orig_html = add_header_to_html(orig_html, header)
        # Native implementation still handles scripts, inline CID assets,
        # Gotenberg, page layout and PDF/A exactly as before.
        return super().generate_pdf_from_html(orig_html, attachments)
