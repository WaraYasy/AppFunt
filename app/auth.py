"""Configuración de Flask-Login: quién es el admin de la sesión actual."""
from flask_login import LoginManager

from app.database import SessionLocal
from app.models.admin import Admin

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str) -> Admin | None:
    return SessionLocal().get(Admin, user_id)


def init_app(app):
    login_manager.init_app(app)
