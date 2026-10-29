# 0.3.1 time-zone validation

Version `0.3.1` removes the HTML header's hardcoded Europe/Berlin zone. The parser uses the running Paperless Django `TIME_ZONE` setting, with UTC if missing/empty. Paperless itself uses UTC when `PAPERLESS_TIME_ZONE` is absent. The formatter receives an explicit time-zone object and remains independent of Django; direct standalone use defaults to UTC.

## Offline regression checks

78 tests cover the existing HTML/mail/i18n behavior, configured Berlin and New York, Kathmandu's fractional offset, both New York DST transitions and a previous-calendar-day conversion. Parser tests use Django/native-parser doubles to verify effective-setting precedence over a conflicting raw environment value, missing/empty/default UTC behavior, and independent English/German labels. Those offline tests do not establish live compatibility.

## Real-stack release gate

The [integration workflow](../.github/workflows/integration.yml) builds one shared candidate wheel and tests:

| Scenario | Header language | Paperless time zone |
| --- | --- | --- |
| `en` | English, plugin language unset | Europe/Berlin, explicit |
| `de` | German | Europe/Berlin, explicit |
| `en-new-york` | English, plugin language unset | America/New_York, explicit |
| `en-utc-default` | English, plugin language unset | PAPERLESS_TIME_ZONE absent; effective UTC |

Contributed catalogs automatically receive the same configured-Berlin job. Each scenario starts disposable native/plugin Paperless `3.3.0` stacks with Gotenberg `8.37` and Tika image `3.3.1.0`, records the actual Django `TIME_ZONE` and raw variable presence in both stacks, and verifies 13 successful synthetic documents plus matching rejection of a missing-sender message. Every inserted HTML header must contain the expected localized date converted to the scenario's zone. Original bytes, native searchable text, native plain-text/PDF delegation, images and header placement must remain correct.

A stable tag requires all scenario jobs and the supported-Python unit/package matrix to pass on the final merged commit. The authoritative [v0.3.1 release assets](https://github.com/MarcLeinenDE/paperless-ngx-mail-header/releases/tag/v0.3.1) include `integration-summary.json`, binding each scenario to its exact commit, workflow and the same wheel SHA-256, plus synthetic PDF/PNG evidence and checksums. Read that summary for completed run results rather than treating this test specification alone as evidence of a passing run.

## Scope

All input in this CI workflow is synthetic. The workflow does not change a production installation. REST uploads exercise real Celery consumption, registry selection, Tika indexing and Gotenberg rendering. The PDF attachment is uploaded separately; IMAP fetching/mail-rule extraction, other Paperless versions and production deployment are outside this CI scope. Historical English/German i18n evidence is in [the 0.3.0 report](integration-report-0.3.0.md).

A separate [operator-reported production test of 0.3.1](production-report-0.3.1.md) covers a narrower real HTML newsletter scenario. That report does not turn all CI scenarios into production-verified paths.
