# Release checklist for 0.2.0

The maintainer authorized completing the repository review, merging the reviewed changes and publishing a GitHub release once the checks pass. Production deployment and PyPI upload are outside that authorization.

## Code and provenance

- [x] Compare the supplied production wheel with the initial import.
- [x] Inspect the native parser hooks in Paperless-ngx `v3.3.0` and `v3.3.4`; the native mail parser file is identical in both releases.
- [x] Add regression coverage and fix the mixed-line-separator insertion error and date overflow.
- [x] Keep native mail parsing, CID resources, attachments and conversion delegated upstream.
- [x] Record the final runtime differences in [source-comparison.md](source-comparison.md).
- [x] Distinguish original project licensing from upstream and the historical local MIT notice.
- [x] Include GPL and CC BY-SA license texts and third-party notices in the distributions.

## Automated and package checks

- [x] Run all 40 offline tests locally with Python 3.12.14.
- [ ] Complete the updated CI matrix on Python 3.12, 3.13 and 3.14.
- [x] Build a wheel and source distribution; run exact metadata, entry-point and source-content checks.
- [x] Complete strict package metadata validation with `twine check --strict`.
- [x] Reproduce and inspect the synthetic example using the formatter and a local headless browser.
- [x] Source-check installation commands for a uv environment and the official Docker image; do not claim these are live-tested installation methods.

## Real integration gate

The maintainer selected an existing test instance. Its connection details have not yet been supplied. Do not install the candidate into production to bypass this gate.

Run the [integration matrix](testing.md#minimum-integration-matrix) on that test instance and record exact Paperless, Python, Gotenberg and plugin versions. Compare native and plugin output for HTML-only, plain-text-only, CID images, controlled external images, separate PDF attachments, escaped Unicode headers and the DST boundary. Check original EML preservation, searchable text, document counts and generated PDFs.

- [ ] Access to the authorized test instance confirmed.
- [ ] Candidate wheel installed and selected through the actual parser registry.
- [ ] Integration matrix completed; synthetic evidence reviewed.
- [ ] An anonymized report records results, versions, candidate commit and tested wheel SHA-256.

## Publication

- [ ] Review the final pull request and merge only the checked head.
- [ ] Retrieve build artifacts from CI for the merged commit and verify checksums.
- [ ] Prepare release notes that state the exact evidence and limitations.
- [ ] Publish `v0.2.0` with the tested wheel, source distribution and `SHA256SUMS.txt` only after the integration gate passes.
- [ ] Check the public release and downloaded asset checksums.

A draft release is preparation only. Do not turn it into a stable release or advertise new live compatibility results while the integration gate is pending.
