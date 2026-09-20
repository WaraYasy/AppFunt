"""Controlador para las preferencias de interfaz: idioma y tema."""
from flask import Blueprint, redirect, request, session, url_for

from app.i18n import SUPPORTED_LOCALES
from app.theme import SUPPORTED_THEMES

settings_bp = Blueprint("settings", __name__)


def _volver_a_la_pagina_anterior():
    return redirect(request.referrer or url_for("base.index"))


def _alternar(actual: str, opciones: tuple[str, ...]) -> str:
    """Devuelve la siguiente opción del ciclo (pensado para 2 valores)."""
    restantes = [opcion for opcion in opciones if opcion != actual]
    return restantes[0] if restantes else actual


@settings_bp.route("/preferencias/idioma", methods=["POST"])
def alternar_idioma():
    session["locale"] = _alternar(session.get("locale", SUPPORTED_LOCALES[0]), SUPPORTED_LOCALES)
    return _volver_a_la_pagina_anterior()


@settings_bp.route("/preferencias/tema", methods=["POST"])
def alternar_tema():
    session["theme"] = _alternar(session.get("theme", SUPPORTED_THEMES[0]), SUPPORTED_THEMES)
    return _volver_a_la_pagina_anterior()
