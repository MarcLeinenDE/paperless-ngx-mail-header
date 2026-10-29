# Contributing a language or localization

English is the source language and default output. German is the first shipped translation. Additional languages are welcome through pull requests: add a gettext catalog and its compiled file; no Python language registry or workflow edit is needed.

The plugin uses its own `mail_header` gettext domain so translations are independent of the language selected in the Paperless web interface. Python's standard library reads compiled catalogs at runtime. Babel is a development-only tool.

The test extra pins the catalog compiler version so `.mo` output remains reproducible in contributor environments and CI.

## Add a catalog

From a virtual environment in a repository checkout:

```bash
python -m pip install -e '.[test]'
# Replace fr with your gettext locale, for example pt_BR or zh_Hant.
pybabel init -i src/paperless_ngx_mail_header/locale/mail_header.pot \
  -d src/paperless_ngx_mail_header/locale -D mail_header -l fr
```

Edit `src/paperless_ngx_mail_header/locale/fr/LC_MESSAGES/mail_header.po` using a text editor or a gettext editor such as Poedit. Translate all six entries:

| Entry | Meaning |
| --- | --- |
| `From` | Sender of an email |
| `To` | Email recipient, not the end of a date range |
| `Date` | Email timestamp |
| `Subject` | Email subject |
| `%Y-%m-%d, %H:%M` | Numeric date/time format, described below |
| `ltr`, context `header layout direction` | Exactly `ltr` or `rtl` |

Labels must be single-line plain text without a trailing colon; the renderer adds punctuation and escapes the translated labels. Do not translate the email's original content or address values. Use your public name or GitHub handle in translator metadata; a private email address is not required. Remove fuzzy flags after reviewing the translations.

### Date/time format

Retain all five numeric directives `%Y`, `%m`, `%d`, `%H` and `%M`, in the order suitable for the language. Literal separators and words can be localized. For example, German uses `%d.%m.%Y, %H:%M Uhr`.

Only those directives and `%%` are accepted. Do not use `%b`, `%B`, `%a` or `%p`: those would depend on the worker machine's process locale instead of the selected catalog. The time zone remains Europe/Berlin for all languages.

### Layout direction

Set the contextual `ltr` entry to `rtl` for right-to-left languages. The header uses logical text alignment and isolates each metadata value with `bdi dir="auto"`. Long labels can wrap. Review actual rendered PDFs, particularly mixed-direction email addresses and non-Latin fonts; structural checks cannot establish linguistic accuracy or font coverage.

## Compile and validate

```bash
python scripts/check_translations.py --compile
python scripts/check_translations.py
python -m pytest -q
```

Commit **both** the edited `.po` and generated `.mo`. The `.pot` is the English template; adding a translation does not require changing it. CI rejects missing or fuzzy entries, invalid dates/direction, stale compiled files and missing package resources. Every contributed catalog is discovered automatically and receives its own disposable real Paperless integration job, using the same wheel as every other locale.

Open a pull request describing the language/region, whether you are a fluent speaker, and any translation choices. Review the synthetic PDF/PNG artifacts from the `Real Paperless integration` workflow. No real email, personal screenshots or device credentials are needed.

## Try the language

Set `PAPERLESS_MAIL_HEADER_LANGUAGE=fr` in the Paperless process/container environment and restart the processes that load the parser. Region separators and case are normalized (`pt_BR` and `pt-BR` refer to the same catalog). A regional code may fall back to its base language if a base catalog exists, such as `de-DE` to `de`. Unsupported languages fall back to English with a warning.

Generated PDFs keep the language chosen at import time. Changing the setting does not retroactively update existing PDFs.

## Maintain the English template

When a source message is intentionally changed, maintainers can extract and update the catalogs:

```bash
pybabel extract --no-location --add-comments=Translators: \
  --msgid-bugs-address https://github.com/MarcLeinenDE/paperless-ngx-mail-header/issues \
  --copyright-holder 'Marc Leinen and contributors' \
  --project paperless-ngx-mail-header \
  -o src/paperless_ngx_mail_header/locale/mail_header.pot src/paperless_ngx_mail_header
pybabel update -i src/paperless_ngx_mail_header/locale/mail_header.pot \
  -d src/paperless_ngx_mail_header/locale -D mail_header
```

Review all changed/fuzzy translations, compile again and include the resulting `.mo` files. Project-authored catalogs are software resources under GPL-3.0-or-later; this guide follows the project's documentation license.
