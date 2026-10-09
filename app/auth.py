"""Flask-Login setup: who is the admin for the current session."""

from flask_login import LoginManager

from app.database import SessionLocal
from app.models.admin import Admin

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id: str) -> Admin | None:
    """Load the admin for the given session id, used by Flask-Login.

    Returns None if the id doesn't match any admin — for example, the
    account was deleted after the session cookie was issued. Flask-Login
    treats a None result as "not logged in" and sends the request to the
    login page, with no error raised.
    """
    return SessionLocal().get(Admin, user_id)


def init_app(app):
    login_manager.init_app(app)
