"""English defaults, German compatibility and catalog-only language contributions."""

import logging
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo

from paperless_ngx_mail_header import i18n
from paperless_ngx_mail_header.formatting import render_header


@pytest.fixture(autouse=True)
def clear_translation_caches(monkeypatch):
    for function in (i18n._catalogs, i18n.resolve_language, i18n.get_translation):
        function.cache_clear()
    yield
    for function in (i18n._catalogs, i18n.resolve_language, i18n.get_translation):
        function.cache_clear()


def mail():
    return SimpleNamespace(
        from_values=SimpleNamespace(full='Sender <sender@example.org>'),
        to_values=[SimpleNamespace(full='Recipient <recipient@example.net>')],
        subject='<Special> & "quoted"',
        date=datetime(2026, 10, 29, 9, 15, tzinfo=timezone.utc),
    )


def test_english_is_default_even_if_environment_or_os_locale_differs(monkeypatch):
    monkeypatch.setenv(i18n.LANGUAGE_ENV, 'de')
    monkeypatch.setenv('LANG', 'de_DE.UTF-8')
    result = render_header(mail())
    for label in ('From:', 'To:', 'Date:', 'Subject:'):
        assert result.count('>' + label + '<') == 1
    assert '2026-10-29, 10:15' in result
    assert 'Uhr' not in result and 'Betreff:' not in result


def test_german_preserves_existing_labels_and_date():
    result = render_header(mail(), language='de')
    for label in ('Von:', 'An:', 'Datum:', 'Betreff:'):
        assert result.count('>' + label + '<') == 1
    assert '29.10.2026, 10:15 Uhr' in result
    assert '&lt;Special&gt; &amp; &quot;quoted&quot;' in result


@pytest.mark.parametrize(('value', 'expected'), [
    (None, 'en'), ('', 'en'), ('  ', 'en'), ('en', 'en'), ('EN_us', 'en'),
    ('de', 'de'), (' DE-de ', 'de'), ('de_AT', 'de'),
])
def test_language_code_normalization(value, expected):
    assert i18n.resolve_language(value) == expected


def test_unsupported_language_falls_back_without_blocking_mail(caplog):
    with caplog.at_level(logging.WARNING):
        result = render_header(mail(), language='not-a-language')
    assert '>Subject:<' in result
    assert 'using English' in caplog.text


def add_test_catalog(tmp_path, monkeypatch, language='fr', direction='ltr'):
    folder = tmp_path / 'locale' / language / 'LC_MESSAGES'
    folder.mkdir(parents=True)
    catalog = Catalog(locale=language)
    for source, translated in {
        'From': 'De & <expéditeur>', 'To': 'À', 'Date': 'Date', 'Subject': 'Objet',
        '%Y-%m-%d, %H:%M': '%d/%m/%Y %H:%M',
    }.items():
        catalog.add(source, translated)
    catalog.add('ltr', direction, context='header layout direction')
    with (folder / 'mail_header.mo').open('wb') as output:
        write_mo(output, catalog)
    monkeypatch.setattr(i18n, 'files', lambda _: tmp_path)
    return folder


def test_a_new_catalog_is_discovered_without_python_registry_changes(tmp_path, monkeypatch):
    add_test_catalog(tmp_path, monkeypatch)
    assert i18n.supported_languages() == ('en', 'fr')
    result = render_header(mail(), language='fr-FR')
    assert '>Objet:<' in result
    assert 'De &amp; &lt;expéditeur&gt;:' in result
    assert '29/10/2026 10:15' in result


def test_rtl_catalog_uses_logical_alignment_and_isolates_values(tmp_path, monkeypatch):
    add_test_catalog(tmp_path, monkeypatch, language='ar', direction='rtl')
    result = render_header(mail(), language='ar')
    assert 'direction:rtl' in result and 'dir="rtl"' in result
    assert 'text-align:start' in result
    assert '<bdi dir="auto">Sender &lt;sender@example.org&gt;</bdi>' in result


def test_damaged_catalog_uses_english_instead_of_failing_import(tmp_path, monkeypatch, caplog):
    folder = add_test_catalog(tmp_path, monkeypatch)
    (folder / 'mail_header.mo').write_bytes(b'bad')
    with caplog.at_level(logging.WARNING):
        result = render_header(mail(), language='fr')
    assert '>Subject:<' in result and 'Could not load header catalog' in caplog.text
