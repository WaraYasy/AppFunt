"""Configuración de Flask-Login: quién es el usuario de la sesión actual."""
from flask_login import LoginManager

from app.database import SessionLocal
from app.models.usuario import Usuario

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str) -> Usuario | None:
    return SessionLocal().get(Usuario, user_id)


def init_app(app):
    login_manager.init_app(app)
