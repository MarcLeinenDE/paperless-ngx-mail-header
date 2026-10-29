"""Check built artifacts without importing Paperless or contacting any service."""

from __future__ import annotations

import configparser
import hashlib
import tarfile
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
    version = project['version']
    artifacts = sorted((ROOT / 'dist').glob('*'))
    wheels = [path for path in artifacts if path.suffix == '.whl']
    sources = [path for path in artifacts if path.name.endswith('.tar.gz')]
    assert len(wheels) == len(sources) == 1, 'Expected exactly one wheel and one sdist'
    with zipfile.ZipFile(wheels[0]) as wheel:
        assert wheel.testzip() is None
        metadata_path, = [name for name in wheel.namelist() if name.endswith('.dist-info/METADATA')]
        metadata = BytesParser().parsebytes(wheel.read(metadata_path))
        assert metadata['Name'] == project['name']
        assert metadata['Version'] == version
        assert metadata['License-Expression'] == project['license']
        assert metadata['Requires-Python'] == project['requires-python']
        assert all('extra ==' in requirement for requirement in metadata.get_all('Requires-Dist', [])), (
            'The plugin must not add runtime dependencies to Paperless'
        )
        entry_path, = [name for name in wheel.namelist() if name.endswith('.dist-info/entry_points.txt')]
        entries = configparser.ConfigParser()
        entries.read_string(wheel.read(entry_path).decode())
        assert entries.sections() == ['paperless_ngx.parsers']
        assert dict(entries['paperless_ngx.parsers']) == {
            'paperless_mail_header': 'paperless_ngx_mail_header.parser:MailHeaderParser'
        }
        for filename in ('__init__.py', 'formatting.py', 'parser.py'):
            assert wheel.read(f'paperless_ngx_mail_header/{filename}') == (
                ROOT / 'src/paperless_ngx_mail_header' / filename
            ).read_bytes(), f'Wheel source mismatch: {filename}'
        for filename in ('LICENSE', 'LICENSES.md', 'THIRD_PARTY_NOTICES.md',
                         'LICENSES/CC-BY-SA-4.0.txt', 'LICENSES/GPL-3.0.txt'):
            assert any(name.endswith('/licenses/' + filename) for name in wheel.namelist())

    with tarfile.open(sources[0]) as source:
        prefix = f'paperless_ngx_mail_header-{version}/'
        for filename in ('LICENSE', 'LICENSES.md', 'THIRD_PARTY_NOTICES.md',
                         'LICENSES/CC-BY-SA-4.0.txt', 'docs/release-checklist.md',
                         'docs/testing.md', 'docs/images/mail-header-example.png',
                         'scripts/verify_distributions.py', 'tests/test_edge_cases.py'):
            assert prefix + filename in source.getnames(), f'Sdist omits {filename}'

    checksums = ''.join(
        f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n'
        for path in (wheels[0], sources[0])
    )
    (ROOT / 'dist/SHA256SUMS.txt').write_text(checksums, encoding='ascii', newline='\n')
    print(f'Version {version}: wheel, sdist, licenses, source and single entry point verified')
    print(checksums, end='')


if __name__ == '__main__':
    main()
