"""Tema visual activo (claro/oscuro), inyectado como global de Jinja.

El valor real se guarda en sesión y se alterna desde
app/controllers/settings_controller.py.
"""
from flask import session

DEFAULT_THEME = "dark"
SUPPORTED_THEMES = ("dark", "light")


def current_theme() -> str:
    theme = session.get("theme", DEFAULT_THEME)
    return theme if theme in SUPPORTED_THEMES else DEFAULT_THEME


def init_app(app):
    @app.context_processor
    def inject_theme():
        return {"current_theme": current_theme()}
