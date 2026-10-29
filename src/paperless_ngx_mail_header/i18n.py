"""Plugin-local gettext catalogs, independent of a browser's active language."""

from __future__ import annotations

import gettext
import logging
import struct
from functools import lru_cache
from importlib.resources import files

LANGUAGE_ENV = "PAPERLESS_MAIL_HEADER_LANGUAGE"
DOMAIN = "mail_header"
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _catalogs():
    root = files(__package__).joinpath("locale")
    if not root.is_dir():
        return {}
    return {
        directory.name.lower().replace("_", "-"): directory.joinpath(
            "LC_MESSAGES", DOMAIN + ".mo"
        )
        for directory in root.iterdir()
        if directory.is_dir()
        and directory.joinpath("LC_MESSAGES", DOMAIN + ".mo").is_file()
    }


def supported_languages() -> tuple[str, ...]:
    return tuple(sorted({"en", *_catalogs()}))


@lru_cache(maxsize=32)
def resolve_language(language: str | None) -> str:
    code = (language or "en").strip().lower().replace("_", "-") or "en"
    supported = supported_languages()
    if code in supported:
        return code
    base = code.split("-", 1)[0]
    if base in supported:
        return base
    logger.warning("Unsupported %s value %r; using English.", LANGUAGE_ENV, code)
    return "en"


@lru_cache(maxsize=32)
def get_translation(language: str = "en") -> gettext.NullTranslations:
    code = resolve_language(language)
    if code == "en":
        return gettext.NullTranslations()
    try:
        with _catalogs()[code].open("rb") as catalog:
            return gettext.GNUTranslations(catalog)
    except (OSError, ValueError, EOFError, struct.error):
        logger.warning("Could not load header catalog %r; using English.", code)
        return gettext.NullTranslations()
