"""Validate every contributed gettext catalog; optionally compile its .mo file."""

from __future__ import annotations

import argparse
import io
import re
from pathlib import Path

from babel.messages.extract import extract_from_dir
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src/paperless_ngx_mail_header"
LOCALE = PACKAGE / "locale"


def validate_catalog(path: Path, required):
    with path.open("rb") as source:
        catalog = read_po(source, locale=path.parents[1].name, abort_invalid=True)
    messages = {(message.context, message.id): message for message in catalog if message.id}
    assert set(messages) == required, f"{path}: missing, obsolete or unexpected messages"
    assert not catalog.fuzzy, f"{path}: fuzzy catalog header"
    for message in messages.values():
        assert message.string and isinstance(message.string, str), f"{path}: untranslated {message.id}"
        assert "fuzzy" not in message.flags, f"{path}: fuzzy {message.id}"
    direction = messages[("header layout direction", "ltr")].string
    assert direction in ("ltr", "rtl"), f"{path}: direction must be ltr or rtl"
    pattern = messages[(None, "%Y-%m-%d, %H:%M")].string
    directives = re.findall(r"%([\s\S])", pattern)
    assert set(directives) <= set("YmdHM%"), f"{path}: use locale-independent numeric date tokens"
    assert set("YmdHM") <= set(directives), f"{path}: incomplete date pattern"
    assert "%" not in re.sub(r"%[YmdHM%]", "", pattern), f"{path}: incomplete date directive"
    for key in ("From", "To", "Date", "Subject"):
        value = messages[(None, key)].string
        assert value.strip() == value and not value.endswith(":") and "\n" not in value, (
            f"{path}: labels must be plain single-line text without a trailing colon"
        )
    errors = list(catalog.check())
    assert not errors, f"{path}: {errors}"
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compile", action="store_true", help="Write compiled catalogs before checking")
    args = parser.parse_args()
    with (LOCALE / "mail_header.pot").open("rb") as template:
        required = {(m.context, m.id) for m in read_po(template) if m.id}
    extracted = {(context, message) for _, _, message, _, context in extract_from_dir(str(PACKAGE))}
    assert required == extracted, "Update mail_header.pot with pybabel extract"
    catalogs = sorted(LOCALE.glob("*/LC_MESSAGES/mail_header.po"))
    assert catalogs, "No translation catalogs found"
    assert set(LOCALE.glob("*/LC_MESSAGES/mail_header.mo")) <= {
        path.with_suffix(".mo") for path in catalogs
    }, "Every compiled catalog must have a matching .po source"
    for path in catalogs:
        assert path.parents[1].name != "en", "English is the source language, not a separate catalog"
        assert re.fullmatch(r"[a-z]{2,3}(?:_[A-Za-z0-9]{2,8})*", path.parents[1].name), (
            f"{path}: use gettext locale names such as de, fr or pt_BR"
        )
        catalog = validate_catalog(path, required)
        compiled = io.BytesIO()
        write_mo(compiled, catalog, use_fuzzy=False)
        target = path.with_suffix(".mo")
        if args.compile:
            target.write_bytes(compiled.getvalue())
        assert target.is_file() and target.read_bytes() == compiled.getvalue(), (
            f"{target}: missing or stale; run python scripts/check_translations.py --compile"
        )
        print(f"{path.parents[1].name}: {len(required)} complete messages; compiled catalog verified")


if __name__ == "__main__":
    main()
