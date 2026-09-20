"""Controlador de autenticación: inicio/cierre de sesión contra Admin."""
from datetime import datetime
from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.database import SessionLocal
from app.forms import LoginForm
from app.i18n import DEFAULT_LOCALE, translate
from app.repositories.admin_repository import AdminRepository

auth_bp = Blueprint("auth", __name__)


def _locale() -> str:
    return session.get("locale", DEFAULT_LOCALE)


def _destino_seguro(candidato: str | None) -> str | None:
    """Solo acepta un `next` que sea una ruta local (evita open redirect
    si alguien arma un link con `?next=https://sitio-malicioso`)."""
    if not candidato:
        return None
    partes = urlsplit(candidato)
    if partes.netloc or partes.scheme:
        return None
    return candidato


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("base.index"))

    db = SessionLocal()
    admin_repo = AdminRepository(db)

    form = LoginForm()
    if form.validate_on_submit():
        admin = admin_repo.get_by_username(form.username.data.strip())
        if admin is not None and admin.check_password(form.password.data):
            login_user(admin, remember=form.remember.data)
            destino = _destino_seguro(request.args.get("next"))
            return redirect(destino or url_for("base.index"))
        form.password.errors.append("auth.error_invalid_credentials")

    status = 400 if form.errors else 200
    return render_template("login.html", form=form, anio_actual=datetime.now().year), status


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash(translate("auth.flash_logged_out", _locale()), "success")
    return redirect(url_for("auth.login"))
