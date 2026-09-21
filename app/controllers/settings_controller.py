"""Controller for UI preferences: language and theme.

Unlike a cycling toggle, each option is picked directly (the view shows
the full list, see sidebar.html) — this also scales fine if
SUPPORTED_LOCALES/SUPPORTED_THEMES grow past 2 values later on.
"""

from flask import Blueprint, abort, redirect, request, session, url_for
from flask_login import login_required

from app.i18n import SUPPORTED_LOCALES
from app.theme import SUPPORTED_THEMES

settings_bp = Blueprint("settings", __name__)


@settings_bp.before_request
@login_required
def _requerir_login():
    """Require a logged-in admin for every route in this blueprint."""


def _volver_a_la_pagina_anterior():
    return redirect(request.referrer or url_for("base.index"))


@settings_bp.route("/preferencias/idioma/<locale>", methods=["POST"])
def elegir_idioma(locale):
    """Set the session language and redirect back. Aborts with 404 if unsupported."""
    if locale not in SUPPORTED_LOCALES:
        abort(404)
    session["locale"] = locale
    return _volver_a_la_pagina_anterior()


@settings_bp.route("/preferencias/tema/<theme>", methods=["POST"])
def elegir_tema(theme):
    """Set the session theme and redirect back. Aborts with 404 if unsupported."""
    if theme not in SUPPORTED_THEMES:
        abort(404)
    session["theme"] = theme
    return _volver_a_la_pagina_anterior()
