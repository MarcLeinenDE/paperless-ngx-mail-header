# Release checklist for 0.2.0

The maintainer authorized review, merge and GitHub publication after the checks. Production deployment and PyPI upload are separate actions.

## Completed checks

- [x] Compare the production `0.1.0` wheel with the initial import and document the two subsequent formatter fixes.
- [x] Inspect native hooks in Paperless `3.3.0` and `3.3.4` without expanding the verified version claim.
- [x] Pass all 40 offline tests, builds, exact distribution checks and strict metadata validation in CI on Python 3.12, 3.13 and 3.14.
- [x] Include project license texts, third-party notices and documentation in distributions.
- [x] Regenerate and inspect the synthetic README image.
- [x] Install the real wheel in a disposable derived Paperless `3.3.0` image with `--no-deps` and verify actual registry selection.
- [x] Complete real REST/worker/Tika/Gotenberg integration against a native baseline: 13 valid imports and one expected invalid-sender rejection per stack.
- [x] Compare original bytes, document counts, searchable text and generated PDFs, including CID/external images and both DST boundaries.
- [x] Visually inspect all 13 synthetic candidate PDFs; record exact versions, candidate commit and wheel hash in the [integration report](integration-report.md).
- [x] Document that IMAP fetching and mail-rule attachment extraction were not tested; no production environment was accessed.

## Publication procedure

1. Review the complete pull request and merge only the latest passing head.
2. Require successful unit/package and real-stack integration workflows on the merged commit. Retrieve the exact wheel, source distribution and checksums from that integration run.
3. Copy its final `summary.json` to the release as `integration-summary.json`; preserve synthetic PDF/PNG evidence in the release evidence archive. Verify that its wheel SHA-256 matches the asset.
4. Write release notes with the verified Paperless version, two formatter fixes and integration scope. Do not imply compatibility with every Paperless 3.x release or a production deployment.
5. Attach all assets, generate their SHA-256 checksums and publish `v0.2.0` only after the final workflow succeeds.
6. Verify the public release target and uploaded asset digests, and confirm that the tag points to the checked merged commit.

The GitHub release is the authoritative publication status. The production `0.1.0` installation must not be replaced automatically.
