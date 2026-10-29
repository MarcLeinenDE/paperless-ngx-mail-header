"""Pure functions that add a small metadata header to HTML e-mails.

The original e-mail HTML is not re-serialized, sanitized or converted here:
Paperless-ngx still runs its native HTML security handling and Gotenberg.
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, tzinfo
from html import escape
from html.parser import HTMLParser

from .i18n import get_translation

_DOCTYPE = re.compile(r"\A(\ufeff?\s*<!doctype\s+html\b[^>]*>)", re.I)


class _InsertPosition(HTMLParser):
    """Locate real tags (not strings/comments), without serializing sender HTML."""

    def __init__(self, source: str):
        super().__init__(convert_charrefs=False)
        self.source = source
        # HTMLParser counts only LF as a new line. str.splitlines() also treats
        # CR, form feeds and Unicode separators as line breaks, shifting offsets.
        self.line_offsets = [0] + [i + 1 for i, char in enumerate(source) if char == "\n"]
        self.body_open: int | None = None
        self.head_close: int | None = None
        self.html_open: int | None = None

    def _index(self):
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == "body" and self.body_open is None:
            self.body_open = self._index() + len(self.get_starttag_text())
        if tag == "html" and self.html_open is None:
            self.html_open = self._index() + len(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag == "head" and self.head_close is None:
            start = self._index()
            m = re.match(r"</head\s*>", self.source[start:], re.I)
            if m:
                self.head_close = start + m.end()



def _value(value: object) -> str:
    text = str(value) if value is not None else ""
    return escape(text.strip() or "—", quote=True)


def _address_list(values: object) -> str:
    return ", ".join(getattr(a, "full", str(a)) for a in (values or []))


def _date_text(value: datetime | None, gettext, timezone: tzinfo) -> str:
    if value is None:
        return "—"
    # The native Paperless parser makes dates timezone-aware before this is called.
    # For direct/standalone use, assume a naive date is in the target local time.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone)
    try:
        local = value.astimezone(timezone)
    except OverflowError:
        # A representable RFC822 date can exceed datetime's range after conversion.
        return "—"
    # Translators: Numeric strftime pattern. Keep %Y, %m, %d, %H and %M.
    return local.strftime(gettext("%Y-%m-%d, %H:%M"))


def render_header(mail: object, *, language: str = "en", timezone: tzinfo = UTC) -> str:
    """Produce four HTML-escaped rows with inline, isolated print styling."""
    translation = get_translation(language)
    gettext = translation.gettext
    # Translators: Use exactly ltr or rtl for the header's writing direction.
    direction = translation.pgettext("header layout direction", "ltr")
    direction = "rtl" if direction == "rtl" else "ltr"
    sender = getattr(getattr(mail, "from_values", None), "full", "")
    recipient = _address_list(getattr(mail, "to_values", None))
    subject = getattr(mail, "subject", "")
    date = _date_text(getattr(mail, "date", None), gettext, timezone)

    entries = (
        (gettext("From"), sender),
        (gettext("To"), recipient),
        (gettext("Date"), date),
        (gettext("Subject"), subject),
    )
    rows = "\n".join(
        '<tr style="vertical-align:top">'
        '<th scope="row" style="width:78px;text-align:start;overflow-wrap:anywhere;'
        'padding:3px 12px 3px 0;font-size:12px;font-weight:600;color:#374151">'
        f"{escape(label, quote=True)}:</th>"
        '<td style="padding:3px 0;font-size:12px;color:#111827;'
        'overflow-wrap:anywhere;word-break:break-word">'
        f'<bdi dir="auto">{_value(value)}</bdi></td></tr>'
        for label, value in entries
    )
    return (
        '<div data-paperless-mail-header="1" '
        'style="display:block;box-sizing:border-box;width:100%;'
        'margin:0 0 16px 0;padding:12px 14px;'
        'background:#f3f4f6;border:1px solid #d1d5db;border-radius:4px;'
        'color:#111827;font:12px/1.4 Arial,Helvetica,sans-serif;'
        f'text-align:start;direction:{direction};break-inside:avoid;page-break-inside:avoid" '
        f'dir="{direction}">'
        '<table role="presentation" style="width:100%;border-collapse:collapse;'
        'border-spacing:0;table-layout:fixed;font:inherit;color:inherit">'
        f"{rows}</table></div>"
    )


def add_header_to_html(original_html: str, header_html: str) -> str:
    """Insert into the real document body without reformatting sender HTML.

    Comments/scripts/quoted attributes that contain fake <body> tags are ignored.
    For HTML fragments, the header is prepended. Existing content stays intact.
    """
    if not original_html:
        return header_html
    locator = _InsertPosition(original_html)
    locator.feed(original_html)
    locator.close()
    position = next((i for i in (locator.body_open, locator.head_close, locator.html_open)
                     if i is not None), None)
    if position is None:
        doc = _DOCTYPE.match(original_html)
        position = doc.end() if doc else 0
    return original_html[:position] + header_html + original_html[position:]
