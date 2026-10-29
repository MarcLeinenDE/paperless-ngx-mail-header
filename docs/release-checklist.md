# Release checklist

Complete these checks before an authorized GitHub release. Production deployment and PyPI upload are separate actions. Use the version in pyproject.toml; never replace an already published tag or release asset with a new candidate.

## Required checks

- Pass the offline test/build/package matrix on supported Python versions.
- Run `python scripts/check_translations.py`: every contributed catalog must be complete, non-fuzzy, current and valid.
- Verify wheel/source contents, bundled translation resources, license files, exact parser entry point and strict metadata checks.
- Run the real-stack workflow using one shared wheel for English (no language setting) and every contributed catalog (explicit setting). Every language job must succeed. Also pass America/New_York and genuinely unset PAPERLESS_TIME_ZONE (UTC default) scenarios, verifying the observed effective settings in both stacks.
- Inspect generated PDFs/PNGs. For 0.3.0 the English and German synthetic matrix passes; see [the i18n report](integration-report-0.3.0.md). New locales need human linguistic and font/layout review.
- Document visible default changes prominently. From 0.3.1 the time zone follows Paperless (UTC if unset); earlier versions hardcoded Europe/Berlin. Starting with 0.3.0, users retain German output by setting `PAPERLESS_MAIL_HEADER_LANGUAGE=de` before restarting the parser-loading services.
- Preserve the native mail/attachment/text-only paths and original input files. Do not access production or real email for release tests.

## Publication procedure

1. Review the PR and merge only its latest fully passing head.
2. Require the unit/package matrix and complete real-stack language matrix on the final merged commit to pass.
3. Download the shared `integration-release` candidate and every `integration-evidence-<scenario>` artifact from that workflow.
4. Verify that all language/time-zone scenario summaries name the final commit, report PASS and bind the same wheel SHA-256. Publish an aggregate `integration-summary.json` and a synthetic PDF/PNG evidence archive with the package assets.
5. Prepare release notes, including supported locales, the English default, the German environment setting and the tested Paperless version. State that IMAP fetching and mail-rule attachment extraction were not exercised.
6. Generate SHA-256 checksums for all assets, tag the checked commit with its version and publish only after these gates pass.
7. Verify the public tag target, uploaded/downloaded asset hashes and summary-to-wheel binding.

The GitHub release is authoritative for publication status. Existing PDFs and the maintainer's production installation are not updated automatically.
