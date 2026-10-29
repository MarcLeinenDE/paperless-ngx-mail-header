from datetime import datetime, timezone
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from paperless_ngx_mail_header.formatting import add_header_to_html, render_header


def mail(**overrides):
    fields = dict(
        from_values=SimpleNamespace(full='Yello Strom GmbH <info@yello.example>'),
        to_values=[SimpleNamespace(full='Max Beispiel <max@example.net>')],
        subject='Kündigungsbestätigung Wärmestrom',
        date=datetime(2026, 10, 29, 7, 15, tzinfo=timezone.utc),
        html='<html><head><style>.mail{color:blue}</style></head><body class="mail">Gute Energie.</body></html>',
        attachments=[object()],
    )
    fields.update(overrides)
    return SimpleNamespace(**fields)


def test_exact_four_fields_and_german_timezone():
    value = render_header(mail(), language='de', timezone=ZoneInfo('Europe/Berlin'))
    for label in ('Von:', 'An:', 'Datum:', 'Betreff:'):
        assert value.count('>' + label + '<') == 1
    assert '29.10.2026, 08:15 Uhr' in value
    assert 'Yello Strom GmbH &lt;info@yello.example&gt;' in value
    assert 'Kündigungsbestätigung Wärmestrom' in value
    assert 'Attachments:' not in value


def test_summer_timezone():
    value = render_header(mail(date=datetime(2026, 8, 2, 12, 10, tzinfo=timezone.utc)),
                          language='de', timezone=ZoneInfo('Europe/Berlin'))
    assert '02.08.2026, 14:10 Uhr' in value


def test_mail_headers_are_escaped():
    value = render_header(mail(subject='<script>alert("bad")</script> & <Kunde>',
                               from_values=SimpleNamespace(full='"Firma" <sales@example.org>')))
    assert '<script>' not in value
    assert '&lt;script&gt;' in value
    assert '&amp;' in value
    assert '&lt;Kunde&gt;' in value
    assert '&quot;Firma&quot;' in value


def test_multiple_recipients():
    value = render_header(mail(to_values=[SimpleNamespace(full='a@example.org'),
                                                SimpleNamespace(full='b@example.org')]))
    assert 'a@example.org, b@example.org' in value


def test_missing_fields_are_graceful():
    value = render_header(mail(from_values=None, to_values=None, subject=None, date=None))
    assert value.count('>—<') == 4


@pytest.mark.parametrize('original', [
    '<!DOCTYPE html><html><head><style>body{margin:3px}</style></head><body class="mail">CONTENT</body></html>',
    '<html><head></head><BODY data-message="a > b"><p>CONTENT</p></BODY></html>',
    '<html><head><meta charset="UTF-8"></head><div>CONTENT</div></html>',
    '<html><div>CONTENT</div></html>',
    '<!doctype html><article>CONTENT</article>',
    '<div>CONTENT</div>',
    '<p>CONTENT</p>',
])
def test_add_header_preserves_original_bytes_order(original):
    header = '<div data-test="header">HEADER</div>'
    result = add_header_to_html(original, header)
    assert result.count(header) == 1
    assert result.replace(header, '') == original
    assert result.index('HEADER') < result.index('CONTENT')


def test_appears_inside_body_not_inside_head():
    original = '<!doctype html><html><head><style>h1 {color:red}</style></head><body><h1>Hello</h1></body></html>'
    result = add_header_to_html(original, 'HEADER')
    assert result.index('</head>') < result.index('HEADER') < result.index('<h1>')


def test_does_not_modify_original_images_or_scripts():
    original = '<html><body><img src="cid:document_logo"><script>alert(1)</script><p>Hi</p></body></html>'
    result = add_header_to_html(original, 'HEADER')
    assert result.replace('HEADER', '') == original
    # Native Paperless still receives and applies its existing script protection.
    assert '<script>alert(1)</script>' in result
    assert 'cid:document_logo' in result


def test_empty_html():
    assert add_header_to_html('', 'HEADER') == 'HEADER'


def test_outlook_comment_does_not_capture_fake_body_tag():
    original = ('<!doctype html><html><!--[if mso]><body class="fake"><![endif]-->'
                '<head><title>X</title></head><body class="real"><p>CONTENT</p></body></html>')
    result = add_header_to_html(original, 'HEADER')
    assert result.replace('HEADER', '') == original
    assert result.index('class="real">') < result.index('HEADER') < result.index('<p>CONTENT</p>')


def test_script_with_string_body_does_not_capture_fake_body_tag():
    original = '<html><head><script>const s = "<body class=fake>";</script></head><body>CONTENT</body></html>'
    result = add_header_to_html(original, 'HEADER')
    assert result.replace('HEADER', '') == original
    assert result.index('</head>') < result.index('HEADER') < result.index('CONTENT')
