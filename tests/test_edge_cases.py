"""Synthetic RFC822 and HTML regression cases; no mail is sent or fetched."""

from datetime import datetime, timezone
from email.message import EmailMessage
from html import escape
from types import SimpleNamespace

import pytest
from imap_tools import MailMessage

from paperless_ngx_mail_header.formatting import add_header_to_html, render_header


@pytest.mark.parametrize("separator", ["\r", "\v", "\f", "\x85", "\u2028", "\u2029"])
def test_html_offsets_follow_lf_lines_even_with_other_separators(separator):
    original = f'<html><!--a{separator}b-->\n<body data-x="a > b">CONTENT</body></html>'
    assert add_header_to_html(original, "HEADER") == original.replace(
        '<body data-x="a > b">', '<body data-x="a > b">HEADER'
    )


@pytest.mark.parametrize("newline", ["\n", "\r\n", "\r"])
def test_multiline_head_and_quoted_body_attributes(newline):
    original = newline.join([
        '<!doctype html><html><head>',
        '<style>body::before { content: "<body>"; }</style>',
        '</head><body title="quoted <body> and >">CONTENT</body></html>',
    ])
    expected = original.replace('and >">', 'and >">HEADER')
    assert add_header_to_html(original, 'HEADER') == expected


def test_date_overflow_is_a_missing_value_instead_of_failing_conversion():
    header = render_header(SimpleNamespace(date=datetime.max.replace(tzinfo=timezone.utc)))
    assert header.count('>—<') == 4


@pytest.mark.parametrize(("date", "expected"), [
    (datetime(2026, 3, 29, 0, 59, tzinfo=timezone.utc), "29.03.2026, 01:59 Uhr"),
    (datetime(2026, 3, 29, 1, 0, tzinfo=timezone.utc), "29.03.2026, 03:00 Uhr"),
    (datetime(2026, 10, 25, 0, 59, tzinfo=timezone.utc), "25.10.2026, 02:59 Uhr"),
    (datetime(2026, 10, 25, 1, 0, tzinfo=timezone.utc), "25.10.2026, 02:00 Uhr"),
    (datetime(2026, 1, 2, 3, 4), "02.01.2026, 03:04 Uhr"),
])
def test_dst_boundaries_and_standalone_naive_date(date, expected):
    assert expected in render_header(SimpleNamespace(date=date), language='de')


@pytest.mark.parametrize("charset", ["utf-8", "iso-8859-1"])
def test_real_rfc822_decoding_of_addresses_subject_and_body(charset):
    message = EmailMessage()
    message['From'] = '"Müller, Anna" <anna@example.org>'
    message['To'] = '"Beispiel, Alex" <alex@example.net>, Team <team@example.org>'
    message['Subject'] = 'Grüße & "Angebot" <2026>'
    message['Date'] = 'Sun, 25 Oct 2026 01:30:00 +0000'
    message.set_content('<html><body>Grüße aus Köln &amp; Bonn</body></html>',
                        subtype='html', charset=charset)
    parsed = MailMessage.from_bytes(message.as_bytes())
    header = render_header(parsed, language='de')
    # Address decoding belongs to imap-tools, just as it does in Paperless.
    # Check that the formatter preserves the parsed value without reparsing it.
    assert escape(parsed.from_values.full, quote=True) in header
    assert 'Müller' in header
    assert 'anna@example.org' in header
    assert 'alex@example.net' in header and 'team@example.org' in header
    assert 'Grüße &amp; &quot;Angebot&quot; &lt;2026&gt;' in header
    assert '25.10.2026, 02:30 Uhr' in header
    assert 'Grüße aus Köln' in parsed.html
    assert add_header_to_html(parsed.html, header).replace(header, '') == parsed.html


def test_incomplete_html_fragment_keeps_its_original_text():
    original = '<div title="unterminated'
    assert add_header_to_html(original, 'HEADER') == 'HEADER' + original
