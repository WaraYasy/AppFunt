"""Active visual theme (dark/light), injected as a Jinja global.

The actual value is stored in the session and switched from
app/controllers/settings_controller.py.
"""
from flask import session

DEFAULT_THEME = "dark"
SUPPORTED_THEMES = ("dark", "light")


def current_theme() -> str:
    """Return the active theme, falling back to DEFAULT_THEME if unset or invalid."""
    theme = session.get("theme", DEFAULT_THEME)
    return theme if theme in SUPPORTED_THEMES else DEFAULT_THEME


def init_app(app):
    @app.context_processor
    def inject_theme():
        return {"current_theme": current_theme()}
