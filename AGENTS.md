<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# Working on Paperless-ngx Mail Header

Read `README.md`, `docs/testing.md`, `docs/installation.md`, `LICENSES.md`, `THIRD_PARTY_NOTICES.md` and the relevant source/tests before editing.

## Architecture

- Keep this a small wrapper around the native Paperless mail parser. Override only the HTML-header insertion hooks.
- Preserve original HTML text except for inserting escaped header markup. Delegate MIME parsing, CID handling, HTML sanitizing, original files, attachments, OCR, thumbnails, PDF/A, Gotenberg, Tika, indexing and workflows to Paperless.
- Leave plain-text-only email on the native path; its template already includes mail metadata.
- Header labels default to English. `PAPERLESS_MAIL_HEADER_LANGUAGE` selects a gettext catalog; German is included. Keep four fields, each exactly once.
- Use the effective Paperless `settings.TIME_ZONE`, with UTC when unset, independently of language. Do not add a separate plugin time-zone setting.
- Do not introduce additional runtime dependencies, JavaScript or network calls in the plugin.
- Check the exact upstream parser contract before changing integration hooks.

## Validation and evidence

- Run relevant offline tests and catalog/package checks for behavior changes. See `docs/testing.md` and `docs/release-checklist.md` for the real-stack release gate.
- New languages must be complete `.po`/`.mo` catalogs, automatically discoverable without a Python registry edit. Follow `docs/translations.md`.
- Exercise representative HTML, escaping, missing fields, recipients, CID resources, text-only delegation and time-zone/DST boundaries when relevant.
- Distinguish offline tests, synthetic real-stack checks and operator-reported production observations. Keep compatibility claims limited to the documented versions and tested paths.
- Do not treat the production report as verification of attachments, other languages or other time zones. See `docs/production-report-0.3.1.md` for its scope.
- Keep examples fully synthetic. Never commit real emails, documents, personal screenshots, credentials, infrastructure identifiers or production logs.

## Licensing

- Project software and CI: `GPL-3.0-or-later`. Documentation and illustrations: `CC-BY-SA-4.0`.
- Preserve valid third-party copyright, license and attribution notices. Record the source and license before importing third-party material.
- Paperless-ngx remains a separate upstream project under its own license; this repository does not redistribute or relicense it.

## Repository workflow

- Use a dedicated branch and pull request. Review the complete diff before merging.
- Pin workflow actions to full upstream commit SHAs with a release-version comment for Dependabot. Keep workflow permissions read-only unless a specific job requires otherwise. Review grouped dependency-update PRs through the normal checks.
- `main` requires the GitHub Actions checks `Unit and package checks` and `Paperless integration checks`. Keep the complete Python and dynamic language/time-zone coverage for relevant changes; only the conservative documentation-only policy in `docs/testing.md` may omit container jobs. Manual release validation must run the full matrix. Do not use CI-skip commit messages in pull requests: skipped workflows cannot satisfy these required checks.
- Perform publication or deployment only within the maintainer's authorized task/session. A GitHub release does not imply a PyPI upload or production deployment.
- Never replace published release tags or assets with a different candidate. Use a new version for code changes and follow `docs/release-checklist.md`.
- Keep documentation in English, concise and consistent with actual behavior. Explain visible default changes and migration settings.
- Keep agent instructions durable and project-focused; do not add conversation transcripts, one-off approvals or private deployment histories.
