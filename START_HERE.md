# START HERE — local Codex preparation

Current source version: `0.3.0`, with English-default gettext i18n and a German catalog. See `docs/translations.md` for adding languages, `docs/configuration.md` for preserving German output on upgrade, and `docs/integration-report-0.3.0.md` for i18n evidence. The notes below describe the original `0.2.0` import.

This is the initial source import for the public GitHub repository `MarcLeinenDE/paperless-ngx-mail-header`. Read `CODEX_HANDOFF.md`, then `AGENTS.md`, then `README.md` before editing.

The current local production release `0.1.0` must not be upgraded without explicit authorization. The maintainer selected `0.2.0` as the first public repository version after comparing its runtime source with the supplied production wheel; see `docs/source-comparison.md`.

The source audit, 40 offline tests, English documentation, license/provenance checks, CI package validation and synthetic example are prepared. The maintainer authorized release preparation and GitHub publication after checks. Real-stack synthetic integration passes in disposable CI; see `docs/integration-report.md`. The final merged candidate must pass the same workflow before the GitHub release assets are published; see `docs/release-checklist.md`.
