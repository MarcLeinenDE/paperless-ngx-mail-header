# Changelog

## [0.3.1] — 2026-10-29

- Replace the hardcoded Europe/Berlin HTML-header time zone with the effective Paperless `settings.TIME_ZONE`, configured via `PAPERLESS_TIME_ZONE`.
- Use UTC when the effective time zone is missing or empty, matching Paperless's unset default. Keep language and time zone independent; no additional plugin environment variable or runtime dependency is introduced.
- Preserve Berlin output when Paperless uses Europe/Berlin. Document the changed behavior for installations using another zone or the UTC default; existing PDFs remain unchanged.
- Add regression coverage for New York DST/date boundaries, fractional offsets, effective-setting precedence and UTC defaults; expand offline coverage to 78 tests.
- Extend the shared-wheel real-stack release gate with configured New York and absent-time-zone/UTC scenarios, alongside every contributed language in Berlin.

## [0.3.0] — 2026-10-29

- Change the inserted HTML header's default language to English: From, To, Date, Subject.
- Add `PAPERLESS_MAIL_HEADER_LANGUAGE`; set it to `de` to keep the previous German labels and date format when upgrading.
- Introduce plugin-local gettext catalogs with German as the first translation. Contributors can add languages via `.po`/`.mo` files without editing a Python language registry or CI matrix.
- Localize the numeric date format, retain Europe/Berlin independently of language, and prepare logical alignment/bidirectional value isolation for future RTL catalogs.
- Validate complete translations, direction/date tokens, compiled catalog freshness and inclusion in wheel/sdist. Test the same candidate wheel in a real Paperless stack for every shipped catalog plus English.
- Verify English/German real-stack imports and German visual compatibility with `0.2.0`; expand offline coverage to 58 cases and document translation-only contribution checks.

## [0.2.0] — 2026-10-29

- First public release, including project documentation and offline CI.
- License project software under GPL-3.0-or-later and project-authored documentation and examples under CC BY-SA 4.0.
- Provide a four-field HTML header while retaining native mail attachment processing.
- Fix HTML insertion offsets when standalone CR, control characters or Unicode separators precede an LF.
- Display an unavailable date rather than failing when timezone conversion overflows Python's supported date range.
- Expand offline tests to 40 cases, including real RFC822 address/charset decoding and DST boundaries.
- Verify real Paperless `3.3.0` imports against a native baseline in disposable CI: 13 successful documents per stack plus identical missing-sender rejection, with PDF/PNG evidence and exact wheel hashes.
- Include documentation and license notices in source distributions; verify package metadata and generate SHA-256 checksums in CI.
- Add a reproducible anonymized header example and development documentation.
- Set package and parser versions to `0.2.0`; require setuptools 77 or newer for the existing SPDX license metadata.
