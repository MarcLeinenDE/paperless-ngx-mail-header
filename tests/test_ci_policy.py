"""Exercise CI skip decisions against real Git changes and the required check."""

import os
from pathlib import Path
import runpy
import shutil
import subprocess
import textwrap

import pytest


ROOT = Path(__file__).resolve().parents[1]
POLICY = runpy.run_path(str(ROOT / 'scripts/ci_changes.py'))


def git(repository, *arguments):
    return subprocess.check_output(
        ['git', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null',
         '-C', str(repository), *arguments], stderr=subprocess.PIPE,
    ).decode().strip()


@pytest.fixture
def repository(tmp_path):
    git(tmp_path, 'init', '-q')
    git(tmp_path, 'config', 'user.name', 'CI policy test')
    git(tmp_path, 'config', 'user.email', 'ci@example.invalid')
    git(tmp_path, 'config', 'core.autocrlf', 'false')
    for name in ('README.md', 'SUPPORT.md', 'docs/testing.md', 'src/plugin.py'):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('Initial content\n', encoding='utf-8')
    git(tmp_path, 'add', '.')
    git(tmp_path, 'commit', '-qm', 'Initial synthetic files')
    return tmp_path, git(tmp_path, 'rev-parse', 'HEAD')


def changed_head(repository):
    git(repository, 'add', '-A')
    git(repository, 'commit', '-qm', 'Synthetic change')
    return git(repository, 'rev-parse', 'HEAD')


def required(repository, base, head, event_name='pull_request'):
    event = {'pull_request': {'base': {'sha': base}, 'head': {'sha': head}},
             'before': base, 'after': head}
    return POLICY['integration_required'](event_name, event, repository)


@pytest.mark.parametrize('event_name', ['pull_request', 'push'])
@pytest.mark.parametrize('operation', ['modify', 'add', 'delete', 'rename'])
def test_regular_document_changes_do_not_need_containers(repository, operation, event_name):
    path, base = repository
    if operation == 'modify':
        (path / 'SUPPORT.md').write_text('Updated text: Grüße\n', encoding='utf-8')
    elif operation == 'add':
        (path / 'docs/new-guide.md').write_text('New documentation\n', encoding='utf-8')
    elif operation == 'delete':
        (path / 'docs/testing.md').unlink()
    else:
        (path / 'docs/testing.md').rename(path / 'docs/renamed-guide.md')
    assert required(path, base, changed_head(path), event_name) is False


@pytest.mark.parametrize('filename', [
    'src/plugin.py', 'tests/test_plugin.py', 'scripts/ci_changes.py',
    '.github/workflows/integration.yml', '.github/dependabot.yml',
    'pyproject.toml', 'MANIFEST.in', 'requirements.txt', '.gitattributes',
    'src/plugin/locale/de/LC_MESSAGES/mail_header.po',
    'src/plugin/locale/de/LC_MESSAGES/mail_header.mo',
    'docs/images/example.png', 'docs/example.py', 'unknown.md',
])
def test_runtime_mixed_and_unknown_changes_require_full_integration(repository, filename):
    path, base = repository
    (path / 'README.md').write_text('Updated documentation\n', encoding='utf-8')
    changed = path / filename
    changed.parent.mkdir(parents=True, exist_ok=True)
    changed.write_text('Changed file\n', encoding='utf-8')
    assert required(path, base, changed_head(path)) is True


def test_renaming_code_to_documentation_still_requires_integration(repository):
    path, base = repository
    (path / 'src/plugin.py').rename(path / 'docs/plugin.md')
    assert required(path, base, changed_head(path)) is True


@pytest.mark.parametrize('content', [b'binary\0data', b'invalid UTF-8: \xff'])
def test_non_text_markdown_requires_integration(repository, content):
    path, base = repository
    (path / 'README.md').write_bytes(content)
    assert required(path, base, changed_head(path)) is True


def test_executable_markdown_requires_integration(repository):
    path, base = repository
    git(path, 'update-index', '--chmod=+x', 'README.md')
    git(path, 'commit', '-qm', 'Make document executable')
    assert required(path, base, git(path, 'rev-parse', 'HEAD')) is True


def test_symlink_markdown_requires_integration(repository):
    path, base = repository
    blob = git(path, 'hash-object', 'src/plugin.py')
    git(path, 'update-index', '--cacheinfo', f'120000,{blob},README.md')
    git(path, 'commit', '-qm', 'Synthetic symlink entry')
    assert required(path, base, git(path, 'rev-parse', 'HEAD')) is True


def test_manual_unknown_empty_and_missing_history_require_integration(repository):
    path, base = repository
    (path / 'README.md').write_text('Documentation only\n', encoding='utf-8')
    head = changed_head(path)
    for event in ('workflow_dispatch', 'schedule', 'unknown'):
        assert required(path, base, head, event) is True
    assert required(path, base, base) is True
    for invalid in ('0' * 40, '1' * 40, '--help', None):
        assert required(path, invalid, head) is True
    for event in ({}, {'pull_request': None}, {'pull_request': []}):
        assert POLICY['integration_required']('pull_request', event, path) is True


def test_main_writes_a_conservative_output_on_bad_event_data(tmp_path, monkeypatch):
    event = tmp_path / 'event.json'
    output = tmp_path / 'output'
    summary = tmp_path / 'summary'
    event.write_text('{broken JSON', encoding='utf-8')
    monkeypatch.setenv('GITHUB_EVENT_PATH', str(event))
    monkeypatch.setenv('GITHUB_OUTPUT', str(output))
    monkeypatch.setenv('GITHUB_STEP_SUMMARY', str(summary))
    POLICY['main']()
    assert output.read_text() == 'integration_required=true\n'
    assert 'Full integration required' in summary.read_text()


@pytest.mark.parametrize(('candidate', 'matrix', 'decision', 'passes'), [
    ('success', 'success', 'true', True),
    ('success', 'skipped', 'false', True),
    ('failure', 'skipped', 'false', False),
    ('cancelled', 'skipped', 'false', False),
    ('skipped', 'skipped', 'false', False),
    ('success', 'failure', 'true', False),
    ('success', 'cancelled', 'true', False),
    ('success', 'skipped', 'true', False),
    ('success', 'success', 'false', False),
    ('success', 'skipped', '', False),
    ('success', 'success', 'unknown', False),
])
def test_actual_required_check_rejects_incomplete_evidence(candidate, matrix, decision, passes):
    workflow = (ROOT / '.github/workflows/integration.yml').read_text(encoding='utf-8')
    gate = textwrap.dedent(workflow.rsplit('        run: |\n', 1)[1])
    if os.name == 'nt':
        bash = Path(shutil.which('git')).resolve().parents[1] / 'bin/bash.exe'
    else:
        bash = shutil.which('bash')
    environment = dict(os.environ, CANDIDATE_BUILD_RESULT=candidate,
                       PAPERLESS_MATRIX_RESULT=matrix, INTEGRATION_REQUIRED=decision)
    environment.pop('BASH_ENV', None)
    result = subprocess.run([str(bash), '-e', '-o', 'pipefail', '-c', gate],
                            env=environment, capture_output=True)
    assert (result.returncode == 0) is passes
