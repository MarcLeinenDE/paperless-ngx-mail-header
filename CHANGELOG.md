# Changelog

## [0.2.0] — initial repository version (no stable release tag yet)

- Prepare public-repository structure, documentation and offline CI.
- Adopt GPL-3.0-or-later for project software and CC BY-SA 4.0 for project-authored documentation and examples.
- Retain the existing four-field header behavior, without changing mail attachment processing.
- Add reproducible anonymized header example and Codex handoff requirements.
- Compare all three Python source files with the supplied production `0.1.0` wheel: the formatter is byte-identical; the parser differs only in version, author and project URL; the package initializer differs only in its docstring and version.
- Set package and parser versions to `0.2.0`; require setuptools 77 or newer for the existing SPDX license metadata.

## [0.1.0] — 2026-10-29 (local/private deployment, not GitHub release)

- Original lightweight parser-plugin implementation.
- Header fields: sender, recipient, Europe/Berlin date and subject.
- Original HTML body and native Paperless rendering pipeline retained.
- Live verified with Paperless-ngx 3.3.0 in the maintainer's environment.
- The originally generated private package metadata stated MIT with the generic attribution `Paperless local integration`. This is historical package provenance; it was not a reused third-party notice.
