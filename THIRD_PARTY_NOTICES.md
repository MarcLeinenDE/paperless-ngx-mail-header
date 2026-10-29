# Third-party notices

## Paperless-ngx

- Upstream: <https://github.com/paperless-ngx/paperless-ngx>
- License: GNU General Public License version 3 (GPLv3)
- Interface source-inspected: Paperless-ngx `3.3.0` and `3.3.4` (identical native mail parser file). Production compatibility observations and synthetic integration tests have separate [scope and limits](docs/testing.md).
- Relationship: the plugin **inherits** the native `paperless.parsers.mail.MailDocumentParser`, calls its methods and registers with `paperless_ngx.parsers`. It does **not** include verbatim upstream Paperless source files.

Paperless-ngx authors retain ownership of their project and trademarks. Its GPL applies to Paperless itself; this extension independently licenses its own project-authored source under GPL-3.0-or-later.

## Gotenberg and Tika

Used **indirectly by Paperless-ngx** for document conversions and text extraction; neither service is bundled by this plugin. Review their upstream licenses and security settings independently:

- Gotenberg: <https://github.com/gotenberg/gotenberg>
- Apache Tika: <https://github.com/apache/tika>

## Attribution policy

Before adding third-party code or images, record exact upstream source, license, imported files, and modifications. Do not import personal email content or brand assets into public examples.
