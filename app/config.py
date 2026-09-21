"""Application configuration, loaded from environment variables."""
import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY no está definida. Configurala en tu archivo .env (ver .env.example) "
        "— firma las cookies de sesión y de 'recordar dispositivo'; sin un valor propio "
        "cualquiera podría falsificarlas."
    )


class Config:
    SECRET_KEY = SECRET_KEY
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Duration of the "remember this device" cookie (login.html,
    # `remember` checkbox). See app/auth.py / app/controllers/auth_controller.py.
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
