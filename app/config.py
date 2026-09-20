import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    # Duración de la cookie de "recordar este dispositivo" (login.html,
    # checkbox `remember`). Ver app/auth.py / app/controllers/auth_controller.py.
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
