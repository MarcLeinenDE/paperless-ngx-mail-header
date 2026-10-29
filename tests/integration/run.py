"""Import synthetic files into two disposable real Paperless stacks and compare PDFs.

Requires requests and PyMuPDF on the test runner, never in the plugin runtime.
Only loopback endpoints of the CI Compose environment are contacted.
"""

from __future__ import annotations

import argparse
import gettext
import hashlib
import json
import os
import struct
import time
import zlib
import zipfile
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from io import BytesIO
from zoneinfo import ZoneInfo
from email import policy
from email.message import EmailMessage
from pathlib import Path

import pymupdf as fitz
import requests

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'work/integration'
REPORT = WORK / 'report'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def marker_png() -> bytes:
    def chunk(kind, payload):
        return struct.pack('!I', len(payload)) + kind + payload + struct.pack(
            '!I', zlib.crc32(kind + payload) & 0xffffffff
        )
    pixels = b''.join(b'\x00' + b'\x18\x78\xd0' * 32 for _ in range(32))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', 32, 32, 8, 2, 0, 0, 0)) + (
        chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')
    )


def prepare() -> None:
    (WORK / 'assets').mkdir(parents=True, exist_ok=True)
    (WORK / 'fixtures').mkdir(exist_ok=True)
    REPORT.mkdir(exist_ok=True)
    png = marker_png()
    (WORK / 'assets/marker.png').write_bytes(png)
    attachment = fitz.open()
    attachment.new_page().insert_text((72, 90), 'SMOKE_PDF_ATTACHMENT_2026')
    pdf = attachment.tobytes()
    attachment.close()
    (WORK / 'fixtures/attachment.pdf').write_bytes(pdf)
    cases = [
        ('html', None), ('text', None), ('cid', None), ('external', None),
        ('html_attachment', None), ('unicode', None), ('mixed_separators', None),
        ('missing_headers', None), ('missing_from', None),
        ('dst_spring_before', ('Sun, 29 Mar 2026 00:59:00 +0000', '29.03.2026, 01:59 Uhr')),
        ('dst_spring_after', ('Sun, 29 Mar 2026 01:00:00 +0000', '29.03.2026, 03:00 Uhr')),
        ('dst_autumn_before', ('Sun, 25 Oct 2026 00:59:00 +0000', '25.10.2026, 02:59 Uhr')),
        ('dst_autumn_after', ('Sun, 25 Oct 2026 01:00:00 +0000', '25.10.2026, 02:00 Uhr')),
    ]
    manifest = []
    for name, date in cases:
        message = EmailMessage(policy=policy.SMTP)
        if name not in ('missing_headers', 'missing_from'):
            message['From'] = 'Anna Beispiel <anna@example.org>'
            message['To'] = 'Alex Beispiel <alex@example.net>, Team <team@example.org>'
            message['Subject'] = 'Grüße & <Marker> "2026"' if name == 'unicode' else f'Smoke {name}'
        elif name == 'missing_headers':
            # From is mandatory upstream; recipient and subject are optional.
            message['From'] = 'Anna Beispiel <anna@example.org>'
        message['Date'] = date[0] if date else 'Thu, 29 Oct 2026 09:15:00 +0000'
        message['Message-ID'] = f'<mail-header-smoke-{name}@example.org>'
        marker = f'BODY_{name}'
        if name == 'text':
            message.set_content(marker + '\nPlain-only message: Grüße aus Köln.')
        else:
            prefix = '<html><head><meta charset="utf-8"></head><body>'
            if name == 'mixed_separators':
                prefix = '<html><!--non-LF\u2028separator-->\n<head></head><body data-x="a > b">'
            content = prefix + '<p>' + marker + '</p><p>Grüße aus Köln &amp; Bonn.</p>'
            if name == 'cid':
                content += '<img src="cid:smoke-logo" width="64" height="64">'
            if name == 'external':
                content += '<img src="http://assets:8080/marker.png" width="64" height="64">'
            content += '</body></html>'
            message.set_content(content, subtype='html', charset='utf-8', cte='quoted-printable')
            if name == 'cid':
                message.add_related(png, maintype='image', subtype='png',
                                    cid='<smoke-logo>', filename='logo.png', disposition='inline')
            if name == 'html_attachment':
                message.add_attachment(pdf, maintype='application', subtype='pdf', filename='attachment.pdf')
        (WORK / f'fixtures/{name}.eml').write_bytes(message.as_bytes())
        manifest.append({'name': name, 'file': f'{name}.eml', 'marker': marker,
                         'date': date[1] if date else '29.10.2026, 10:15 Uhr',
                         'rfc822_date': message['Date'],
                         'expect_rejection': name == 'missing_from'})
    manifest.append({'name': 'attachment_pdf', 'file': 'attachment.pdf',
                     'marker': 'SMOKE_PDF_ATTACHMENT_2026'})
    (WORK / 'fixtures.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'Prepared {len(manifest)} synthetic files; no email is sent or fetched')


def api(port):
    session = requests.Session()
    base = f'http://127.0.0.1:{port}/api/'
    response = session.post(base + 'token/', data={'username': 'smoke',
                            'password': os.environ['SMOKE_PASSWORD']}, timeout=60)
    response.raise_for_status()
    session.headers['Authorization'] = 'Token ' + response.json()['token']
    return session, base


def get_json(session, url):
    response = session.get(url, timeout=60)
    response.raise_for_status()
    return response.json()


def documents(session, base):
    data = get_json(session, base + 'documents/?page_size=100')
    return data['results']


def import_files(session, base, cases):
    assert len(documents(session, base)) == 0, 'Smoke tests require a fresh disposable database'
    for case in cases:
        path = WORK / 'fixtures' / case['file']
        mime = 'application/pdf' if path.suffix == '.pdf' else 'message/rfc822'
        with path.open('rb') as file:
            response = session.post(base + 'documents/post_document/',
                                    data={'title': 'SMOKE_' + case['name']},
                                    files={'document': (path.name, file, mime)}, timeout=90)
        response.raise_for_status()
    deadline = time.monotonic() + 600
    previous_count = -1
    accepted = [case for case in cases if not case.get('expect_rejection')]
    rejected = {case['file'] for case in cases if case.get('expect_rejection')}
    while time.monotonic() < deadline:
        docs = documents(session, base)
        if len(docs) != previous_count:
            print(f'Imported {len(docs)}/{len(accepted)} valid synthetic documents', flush=True)
            previous_count = len(docs)
        tasks = get_json(session, base + 'tasks/?page_size=100')
        if isinstance(tasks, dict):
            tasks = tasks.get('results', [])
        (REPORT / f'tasks-{base.split(":")[2].split("/")[0]}.json').write_text(
            json.dumps(tasks, indent=2), encoding='utf-8'
        )
        failures = [task for task in tasks
                    if task.get('task_type') == 'consume_file'
                    and str(task.get('status', '')).lower() in ('failure', 'failed', 'revoked')]
        unexpected = [task for task in failures if task.get('input_data', {}).get('filename') not in rejected]
        assert not unexpected, f'Synthetic import failed: {unexpected}'
        expected = {task['input_data']['filename']: task for task in failures}
        for task in expected.values():
            assert "Missing 'from'" in str(task.get('result_data')), 'Unexpected invalid-mail failure'
        if len(docs) == len(accepted) and set(expected) == rejected:
            return {doc['title'].removeprefix('SMOKE_'): doc for doc in docs}
        time.sleep(3)
    raise TimeoutError(f'Only {len(documents(session, base))}/{len(accepted)} valid imports completed')


def download(session, url):
    response = session.get(url, timeout=90)
    response.raise_for_status()
    return response.content


def version(kind):
    lines = (WORK / f'{kind}-version.txt').read_text().splitlines()
    return json.loads(next(line.split('SMOKE_VERSION=', 1)[1]
                           for line in lines if 'SMOKE_VERSION=' in line))


def run() -> None:
    cases = json.loads((WORK / 'fixtures.json').read_text())
    accepted = [case for case in cases if not case.get('expect_rejection')]
    observed = {}
    language = os.environ.get('SMOKE_LANGUAGE', 'en')
    wheel, = (ROOT / 'dist').glob('*.whl')
    translation = gettext.NullTranslations()
    with zipfile.ZipFile(wheel) as package:
        metadata_path, = [name for name in package.namelist() if name.endswith('.dist-info/METADATA')]
        plugin_version = BytesParser().parsebytes(package.read(metadata_path))['Version']
        if language != 'en':
            path, = [name for name in package.namelist() if name.endswith('/LC_MESSAGES/mail_header.mo')
                     and name.split('/')[-3].replace('_', '-').lower() == language]
            translation = gettext.GNUTranslations(BytesIO(package.read(path)))
    labels = [translation.gettext(label) + ':' for label in ('From', 'To', 'Date', 'Subject')]
    if language == 'de':
        assert labels == ['Von:', 'An:', 'Datum:', 'Betreff:']
    for kind, port in [('native', 8000), ('plugin', 8001)]:
        session, base = api(port)
        docs = import_files(session, base, cases)
        assert len(docs) == len(accepted)
        (REPORT / kind).mkdir(parents=True, exist_ok=True)
        results = {}
        for case in accepted:
            name = case['name']
            doc = docs[name]
            original = download(session, base + f'documents/{doc["id"]}/download/?original=true')
            assert original == (WORK / 'fixtures' / case['file']).read_bytes(), f'{kind}/{name}: original changed'
            pdf = download(session, base + f'documents/{doc["id"]}/preview/')
            assert pdf.startswith(b'%PDF'), f'{kind}/{name}: preview is not a PDF'
            (REPORT / kind / f'{name}.pdf').write_bytes(pdf)
            with fitz.open(stream=pdf, filetype='pdf') as rendered:
                text = '\n'.join(page.get_text() for page in rendered)
                assert case['marker'] in text, f'{kind}/{name}: body missing from PDF'
                image_count = sum(len(page.get_images()) for page in rendered)
                if name in ('cid', 'external'):
                    assert image_count > 0, f'{kind}/{name}: image missing from PDF'
                if kind == 'plugin' and name not in ('text', 'attachment_pdf'):
                    for label in labels:
                        assert text.count(label) == 1, f'{name}: missing or duplicate {label}'
                    date = parsedate_to_datetime(case['rfc822_date']).astimezone(ZoneInfo('Europe/Berlin'))
                    date_text = date.strftime(translation.gettext('%Y-%m-%d, %H:%M'))
                    if language == 'de':
                        assert date_text == case['date'], 'German legacy date style changed'
                    assert date_text in text, f'{name}: incorrect localized Berlin timestamp'
                    header_y = rendered[0].search_for(labels[0])[0].y0
                    body_y = rendered[0].search_for(case['marker'])[0].y0
                    assert header_y < body_y, f'{name}: header is below body'
                    if name == 'unicode':
                        assert 'Grüße & <Marker> "2026"' in text
                rendered[0].get_pixmap(matrix=fitz.Matrix(1, 1)).save(REPORT / kind / f'{name}.png')
                results[name] = {'original_sha256': sha(original), 'pdf_sha256': sha(pdf),
                                 'pdf_text': text, 'searchable_text': doc['content'],
                                 'pages': len(rendered), 'images': image_count}
        observed[kind] = results
        print(f'{kind}: {len(docs)} original files and real PDF previews verified')

    for case in accepted:
        name = case['name']
        native = observed['native'][name]
        plugin = observed['plugin'][name]
        assert native['original_sha256'] == plugin['original_sha256']
        assert native['searchable_text'] == plugin['searchable_text'], f'{name}: indexing changed'
        if name in ('text', 'attachment_pdf'):
            assert native['pdf_text'] == plugin['pdf_text'], f'{name}: native output changed'
            assert native['pages'] == plugin['pages']
    versions = {kind: version(kind) for kind in ('native', 'plugin')}
    assert versions['native']['parser'] == 'Paperless-ngx Mail Parser'
    assert versions['plugin']['parser'] == 'Paperless-ngx Mail Header'
    assert versions['plugin']['parser_version'] == plugin_version
    report = {'status': 'PASS', 'commit': os.environ.get('GITHUB_SHA', 'local'),
              'workflow_run': os.environ.get('GITHUB_RUN_ID', 'local'),
              'wheel_sha256': sha(wheel.read_bytes()), 'versions': versions,
              'header_language': language,
              'dependencies': {'gotenberg': '8.37', 'tika_image': '3.3.1.0', 'broker_image': 'valkey:9-alpine'},
              'documents_per_stack': len(accepted), 'results': observed,
              'expected_rejections_per_stack': {'missing_from.eml': "Missing 'from'"},
              'scope': 'Real REST upload, Celery consumption, registry, Tika indexing and Gotenberg PDF rendering. PDF attachment uploaded separately; external IMAP fetching and mail-rule extraction are not exercised. All input is synthetic.'}
    (REPORT / 'summary.json').write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                       encoding='utf-8')
    print(f'PASS: {len(accepted)} valid cases plus matching mandatory-From rejection per real stack')


if __name__ == '__main__':
    arguments = argparse.ArgumentParser()
    arguments.add_argument('--prepare', action='store_true')
    args = arguments.parse_args()
    prepare() if args.prepare else run()
