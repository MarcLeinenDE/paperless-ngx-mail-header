# Codex handoff — initial repository import

## Objective

The maintainer authorized creation of the public repository `MarcLeinenDE/paperless-ngx-mail-header` and the initial `0.2.0` import on 2026-10-29. Import changes through a dedicated branch and pull request before merging to `main`. The maintainer subsequently authorized completing the release checks, merging reviewed changes and publishing the GitHub release. PyPI publication and production deployment remain separate actions. Preserve behavior of the working local `0.1.0` plugin. Do not introduce broader email attachment, OCR or conversion features.

## Production reference reported by the maintainer (2026-10-29)

Subsequent maintainer direction for `0.3.0`: make English the default inserted-header language, add German through `PAPERLESS_MAIL_HEADER_LANGUAGE=de`, and let contributors add further gettext localizations through catalog-only PRs. This explicitly replaces the original German-only output rule; native mail handling and production-deployment restrictions remain in place.

Subsequent maintainer direction for `0.3.1`: use Paperless's effective `settings.TIME_ZONE` and fall back to UTC when unset, matching Paperless. Language remains independent of time zone. No separate plugin time-zone variable is requested.

- Paperless-ngx: `3.3.0`; the production environment itself is outside this repository.
- Consumer, Celery task worker and webserver load parser plugins.
- Current production plugin, per subsequent maintainer report: `paperless-ngx-mail-header==0.3.1`, upgraded from `0.1.0` on 2026-10-29; registry selected `Paperless-ngx Mail Header` version `0.3.1`. See [the production report](docs/production-report-0.3.1.md) for exact versions, observed HTML newsletter behavior and untested paths.
- The maintainer reported a successful real HTML email import and visually checked the German four-field header, Berlin-local date, Unicode/emoji, HTML layout and external images. No private screenshots or messages are included here. This is maintainer-reported evidence, not a fresh production inspection by the repository agent.
- **Do not embed local host/IP, email addresses, logs or personal screenshots in the public repository.**

## Grounded starting facts

- The current implementation inherits from the native parser and overrides `generate_pdf()` and `generate_pdf_from_html()`. The formatting logic is pure Python.
- The original local `0.1.0` source ZIP was reviewed and 22 unit tests passed in this working environment. Those tests use a native parser double and must not be marketed as integrated tests.
- The old `0.1.0` files contained a generic MIT LICENSE generated locally, **not imported from upstream**. The prepared public source is `0.2.0` with GPL-3.0-or-later for own code.
- Maintainer decision on 2026-10-29: start the repository at `0.2.0` if runtime code matches production. Comparison with the supplied `0.1.0` wheel confirmed that condition at the initial import; two later formatter edge-case fixes are documented separately; see `docs/source-comparison.md`. This selects the initial repository version and does not establish new live integration results.
- The project follows the documentation and licensing pattern of `MarcLeinenDE/nr2301-api`, `nr2301-python`, and `w1-nfc-reader`.

## Work items for Codex after authorization

1. Audit the repo source and tests, checking exact Paperless `3.3.0` contracts and compatibility with newer supported releases using source evidence, not assumptions.
2. Add missing edge-case unit tests (HTML parser oddities, quoted strings, RFC822 addressing, date extremes, charset issues).
3. Add offline CI test/build jobs and release gates; ensure wheel metadata and entrypoint are correct.
4. Review the screenshot generator and keep the example fully synthetic; verify it represents the actual formatter.
5. Verify README statements (notably HTML-only mail rules, plain-text-only fallback, native attachment flow) against implementation.
6. Complete licensing/provenance audit, especially no imported upstream code or screenshot assets.
7. Validate the installation instructions for Docker and non-Docker/uv environments; production upgrades always require backup and explicit authorization.
8. Initial repository version `0.2.0` has been selected by the maintainer after the source comparison. Complete real integration tests before a stable release tag, and record release checksums for the final published artifacts.
9. Repository creation and the initial import are authorized. Keep the complete source import in a review pull request before merging to `main`. A GitHub release is now authorized after the release checks; no PyPI upload or production deployment is implied.

## Acceptance criteria

- Unit tests pass on supported Python versions.
- Wheel builds and advertises exactly one parser entrypoint for `.eml`.
- No non-HTML mail processing regressions.
- Native PDF render and attachment handling are delegated to upstream.
- New header uses four fields; correct timezone, escaping and unchanged HTML body.
- README image is self-contained, reproducible, anonymous.
- Legal text and notices distinguish project source from Paperless source.
- No repository creation, push or production change before explicit user instruction.

## Known non-goals

- Mail fetching, parsing, filtering or workflow changes.
- Additional attachments merging or OCR modifications.
- Gotenberg image-fetch config changes (document optional safe settings only).
- Shipping a Paperless-ngx fork.

## Required manual integration smoke tests before a stable tag

With consent on a test instance: HTML-only email, plain-text-only email, HTML with CID images, HTML with external images, HTML plus PDF attachment processed separately, UTF-8 German special characters, timestamp across DST boundary; compare original `.eml`, searchable text, document count and generated PDF against native parser.
