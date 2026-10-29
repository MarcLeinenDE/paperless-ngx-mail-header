<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->
# AGENTS.md — Paperless-ngx Mail Header

This file contains repository-wide working rules for Codex and other coding agents.

## Read first

1. `CODEX_HANDOFF.md`
2. `README.md`
3. `docs/testing.md`
4. `docs/installation.md`
5. `LICENSES.md` and `THIRD_PARTY_NOTICES.md`
6. Source and tests under `src/` and `tests/`

## Invariants / architecture

- This is a **small wrapper around the built-in Paperless mail parser**, not a replacement email engine.
- Override only the HTML-header insertion hooks needed for metadata display.
- Preserve original HTML text exactly except for inserting header markup. Do not reserialize the message, combine the header with CSS resources, reimplement CID handling, or rewrite HTML sanitizing.
- Keep original `.eml`, mail rules, attachment filters and imports, OCR, thumbnails, PDF/A, Gotenberg, Tika and workflows on their native Paperless paths.
- Text-only mail must retain native behavior; the native template already provides header metadata.
- Header labels are `Von`, `An`, `Datum`, `Betreff`, exactly once each, shown in the Europe/Berlin timezone.
- Escape untrusted header values; do not introduce JavaScript, networking or additional runtime dependencies.
- Consider compatibility with the exact Paperless parser methods and their upstream changes before modifying anything.
- New features are opt-in and must not silently change existing production behaviors.

## Evidence and tests

- Treat the installed local plugin `0.1.0` as a proven production reference. **Do not replace it automatically.**
- Current source tree is `0.2.0`, selected by the maintainer as the first public repository version, **not released**. The runtime source comparison is recorded in `docs/source-comparison.md`.
- Run offline tests before suggesting integration. Mark fake/mock-based tests honestly; passing unit tests does not establish end-to-end compatibility.
- Test HTML documents with complex `<head>` and `<body>` attributes, fake markup inside comments/scripts, inline CIDs, missing fields, multiple recipients, escaping, and daylight-saving time.
- Add a separate integration test checklist; never send or fetch real email without explicit user authorization.
- Compatibility labels must distinguish `LIVE_VERIFIED`, `UNIT_TESTED`, `NOT_VERIFIED`, `KNOWN_ISSUE`.

## Licensing and provenance

- Project-authored software and CI: `GPL-3.0-or-later`; documentation/illustration: `CC-BY-SA-4.0`.
- Paperless-ngx itself is GPLv3, is not redistributed or relicensed by this project.
- The earlier local `0.1.0` package contained a generic MIT license. It was **our original generated packaging**, not a third-party MIT dependency. Keep historical provenance correct.
- Do not copy code from the `toweosp` alternative parser unless its exact license and attribution obligations are deliberately reviewed.

## Repository operations and publication gate

- **No remote repository creation, push, release, public package publish, or production deployment without explicit user authorization.**
- The maintainer authorized the public repository and initial `0.2.0` import on 2026-10-29. Use a dedicated branch and pull request for review. The maintainer subsequently authorized completing release preparation, merging reviewed changes and publishing the GitHub release once checks pass. This does not authorize a PyPI upload or production deployment. The integration release gate below still applies.
- Local development/build/test and drafting docs are permitted.
- Follow the maintainer's established convention: isolated development branch, changes reviewed before `main`, versioned tags after release checks.
- Never commit real `.eml`, private screenshots, credentials, infrastructure names/IPs, or debug logs.

## Documentation style

- English-first technical README and docs; factual claims must match tests.
- Reuse visual/design conventions from `MarcLeinenDE/nr2301-api`, `nr2301-python` and `w1-nfc-reader` without copying private data.
- Concise scope, clear status, installation, rollback, privacy/security, license and disclaimer sections.
- Keep example header PNG fully synthetic and reproducible from its generator.
