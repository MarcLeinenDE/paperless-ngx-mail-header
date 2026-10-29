"""Unit contract with Paperless native class replaced by a small test double.

It verifies delegation, not a full Gotenberg/Tika/Paperless integration.
"""
import importlib
import sys
from datetime import datetime, timezone
from types import ModuleType, SimpleNamespace

import pytest


@pytest.fixture
def parser_class(monkeypatch):
    monkeypatch.delenv('PAPERLESS_MAIL_HEADER_LANGUAGE', raising=False)
    class NativeMailParser:
        @classmethod
        def supported_mime_types(cls):
            return {'message/rfc822': '.eml'}

        def generate_pdf(self, mail_message, pdf_layout=None):
            self.layout_seen = pdf_layout
            if mail_message.html:
                return self.generate_pdf_from_html(mail_message.html, mail_message.attachments)
            return ('text-native', mail_message.text, mail_message.attachments)

        def generate_pdf_from_html(self, orig_html, attachments):
            if getattr(self, 'force_exception', False):
                raise RuntimeError('native conversion failed')
            return ('native-html', orig_html, attachments)

    packages = {name: ModuleType(name) for name in ('paperless', 'paperless.parsers', 'paperless.parsers.mail')}
    packages['paperless'].__path__ = []
    packages['paperless.parsers'].__path__ = []
    packages['paperless.parsers.mail'].MailDocumentParser = NativeMailParser
    for name, module in packages.items():
        monkeypatch.setitem(sys.modules, name, module)
    # Do not keep a cached plugin class with a different native class.
    sys.modules.pop('paperless_ngx_mail_header.parser', None)
    module = importlib.import_module('paperless_ngx_mail_header.parser')
    yield module.MailHeaderParser
    sys.modules.pop('paperless_ngx_mail_header.parser', None)


def message(html='<html><body>MAIL BODY</body></html>', text='TEXT BODY', attachments=None):
    return SimpleNamespace(
        html=html, text=text, attachments=attachments if attachments is not None else [object()],
        date=datetime(2026, 10, 29, 7, 49, tzinfo=timezone.utc),
        from_values=SimpleNamespace(full='From <from@example.net>'),
        to_values=[SimpleNamespace(full='recipient@example.net')],
        subject='Subject',
    )


def test_only_eml_supported_and_preferred_over_native(parser_class):
    assert parser_class.score('message/rfc822', 'email.eml') == 20
    for mime in ['application/pdf', 'text/html', 'text/plain', 'image/png']:
        assert parser_class.score(mime, 'sample') is None
    assert parser_class.supported_mime_types() == {'message/rfc822': '.eml'}


def test_html_conversion_delegates_to_native_with_untouched_attachments(parser_class):
    parser = parser_class()
    m = message()
    result = parser.generate_pdf(m, pdf_layout=3)
    assert result[0] == 'native-html'
    assert result[2] is m.attachments
    assert result[1].count('data-paperless-mail-header="1"') == 1
    assert result[1].replace(result[1][result[1].index('<div data-paperless-mail-header'):result[1].index('</table></div>') + len('</table></div>')], '') == m.html
    assert parser.layout_seen == 3
    assert parser._header_mail_message is None


def test_text_mail_entirely_native(parser_class):
    m = message(html='', text='A <B> & üäö')
    parser = parser_class()
    result = parser.generate_pdf(m, pdf_layout=3)
    assert result == ('text-native', m.text, m.attachments)
    assert parser._header_mail_message is None


def test_native_html_converter_called_unmodified_without_context(parser_class):
    parser = parser_class()
    sample = '<html><body>raw HTML</body></html>'
    attachments = [object()]
    assert parser.generate_pdf_from_html(sample, attachments) == ('native-html', sample, attachments)


def test_no_context_leak_after_exception(parser_class):
    parser = parser_class()
    parser.force_exception = True
    with pytest.raises(RuntimeError, match='native conversion failed'):
        parser.generate_pdf(message())
    assert parser._header_mail_message is None


@pytest.mark.parametrize(('language', 'expected', 'unexpected'), [
    (None, 'Subject:', 'Betreff:'),
    ('de', 'Betreff:', 'Subject:'),
    ('de-DE', 'Betreff:', 'Subject:'),
    ('en', 'Subject:', 'Betreff:'),
])
def test_worker_environment_selects_header_language(parser_class, monkeypatch, language, expected, unexpected):
    if language is not None:
        monkeypatch.setenv('PAPERLESS_MAIL_HEADER_LANGUAGE', language)
    result = parser_class().generate_pdf(message())
    assert '>' + expected + '<' in result[1]
    assert '>' + unexpected + '<' not in result[1]
