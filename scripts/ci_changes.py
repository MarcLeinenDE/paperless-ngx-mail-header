"""Skip container tests only for an unambiguous documentation-only Git diff."""

from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess


ROOT_DOCUMENTS = frozenset({
    'AGENTS.md', 'CHANGELOG.md', 'CONTRIBUTING.md', 'LICENSES.md', 'README.md',
    'SECURITY.md', 'SUPPORT.md', 'THIRD_PARTY_NOTICES.md',
})


def git(repository: Path, *arguments: str) -> bytes:
    return subprocess.run(
        ['git', '-C', str(repository), *arguments], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
    ).stdout


def is_document(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return path in ROOT_DOCUMENTS or (
        len(parts) >= 2 and parts[0] == 'docs' and path.endswith('.md')
        and all(part not in ('.', '..') for part in parts)
    )


def documentation_only(repository: Path, base: str, head: str) -> bool:
    if not all(isinstance(sha, str) and re.fullmatch(r'[0-9a-f]{40}', sha)
               and sha != '0' * 40 for sha in (base, head)):
        return False
    # A two-commit comparison is conservative when a PR base advances: extra
    # upstream changes can require tests, but cannot hide a changed runtime file.
    records = git(repository, 'diff', '--raw', '-z', '--no-renames',
                  '--no-ext-diff', base, head, '--').split(b'\0')
    if records == [b'']:
        return False
    if records[-1] != b'' or len(records) % 2 != 1:
        return False
    for index in range(0, len(records) - 1, 2):
        metadata = records[index].split()
        path = records[index + 1].decode('utf-8')
        if len(metadata) != 5 or metadata[4] not in (b'A', b'M', b'D'):
            return False
        modes = (metadata[0].removeprefix(b':'), metadata[1])
        if not is_document(path) or any(mode not in (b'000000', b'100644') for mode in modes):
            return False
        # Reject symlinks, executable documents, binary data and invalid UTF-8.
        for revision, mode in zip((base, head), modes):
            if mode != b'000000':
                content = git(repository, 'show', f'{revision}:{path}')
                if b'\0' in content:
                    return False
                content.decode('utf-8')
    return True


def integration_required(event_name: str, event: dict, repository: Path) -> bool:
    try:
        if event_name == 'pull_request':
            base = event['pull_request']['base']['sha']
            head = event['pull_request']['head']['sha']
        elif event_name == 'push':
            base, head = event['before'], event['after']
        else:
            return True  # Manual release validation always runs the full matrix.
        return not documentation_only(repository, base, head)
    except (KeyError, TypeError, ValueError, OSError, subprocess.SubprocessError):
        return True  # Missing history, malformed input or Git errors never skip tests.


def main() -> None:
    try:
        event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
        required = integration_required(os.environ.get('GITHUB_EVENT_NAME', ''), event, Path.cwd())
    except (KeyError, ValueError, OSError):
        required = True
    value = str(required).lower()
    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
        output.write(f'integration_required={value}\n')
    explanation = (
        'Full integration required (runtime-affecting, manual, empty or unclassified change).'
        if required else 'Only allowed regular Markdown documents changed; container tests not required.'
    )
    print(explanation)
    if summary := os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(summary, 'a', encoding='utf-8') as output:
            output.write(f'### Integration policy\n\n{explanation}\n')


if __name__ == '__main__':
    main()
