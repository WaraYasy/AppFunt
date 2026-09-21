"""Translation system based on one JSON file per language.

Each language lives in its own file inside app/translations/ (e.g.
es.json, en.json). Templates read strings through the `t('section.key')`
function, injected as a Jinja global.
"""

import json
from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).resolve().parent / "translations"
DEFAULT_LOCALE = "es"
SUPPORTED_LOCALES = ("es", "en")

_cache: dict[str, dict] = {}


def _load(locale: str) -> dict:
    if locale not in _cache:
        path = TRANSLATIONS_DIR / f"{locale}.json"
        with path.open(encoding="utf-8") as f:
            _cache[locale] = json.load(f)
    return _cache[locale]


def translate(key: str, locale: str = DEFAULT_LOCALE) -> str:
    """Resolve a dot-notation key (e.g. 'nav.dashboard') to its translated string.

    Falls back to DEFAULT_LOCALE if `locale` isn't supported, and returns
    the key itself if it's missing from the translation file.
    """
    locale = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    value: dict | str = _load(locale)

    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return key
        value = value[part]

    return value


def init_app(app):
    """Register `t()` and `current_locale` as globals available in every template."""

    @app.context_processor
    def inject_translator():
        from flask import session

        locale = session.get("locale", DEFAULT_LOCALE)
        return {
            "t": lambda key: translate(key, locale),
            "current_locale": locale,
            "supported_locales": SUPPORTED_LOCALES,
        }
