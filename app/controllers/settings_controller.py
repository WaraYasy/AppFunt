"""Controlador para las preferencias de interfaz: idioma y tema.

A diferencia de un toggle ciclado, cada opción se elige de forma directa
(la vista muestra el listado completo, ver sidebar.html) — esto también
escala solo si el día de mañana SUPPORTED_LOCALES/SUPPORTED_THEMES crecen
más allá de 2 valores.
"""
from flask import Blueprint, abort, redirect, request, session, url_for
from flask_login import login_required

from app.i18n import SUPPORTED_LOCALES
from app.theme import SUPPORTED_THEMES

settings_bp = Blueprint("settings", __name__)


@settings_bp.before_request
@login_required
def _requerir_login():
    pass


def _volver_a_la_pagina_anterior():
    return redirect(request.referrer or url_for("base.index"))


@settings_bp.route("/preferencias/idioma/<locale>", methods=["POST"])
def elegir_idioma(locale):
    if locale not in SUPPORTED_LOCALES:
        abort(404)
    session["locale"] = locale
    return _volver_a_la_pagina_anterior()


@settings_bp.route("/preferencias/tema/<theme>", methods=["POST"])
def elegir_tema(theme):
    if theme not in SUPPORTED_THEMES:
        abort(404)
    session["theme"] = theme
    return _volver_a_la_pagina_anterior()
