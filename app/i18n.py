"""Sistema de traducciones basado en archivos JSON por idioma.

Cada idioma vive en su propio archivo dentro de app/translations/
(por ejemplo es.json, en.json). Las plantillas acceden a las cadenas
mediante la función `t('seccion.clave')`, inyectada como global de Jinja.
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
    """Resuelve una clave con notación de puntos (ej. 'nav.dashboard')."""
    locale = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    value: dict | str = _load(locale)

    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return key
        value = value[part]

    return value


def init_app(app):
    """Registra `t()` y `current_locale` como disponibles en todas las plantillas."""

    @app.context_processor
    def inject_translator():
        from flask import session

        locale = session.get("locale", DEFAULT_LOCALE)
        return {
            "t": lambda key: translate(key, locale),
            "current_locale": locale,
        }
