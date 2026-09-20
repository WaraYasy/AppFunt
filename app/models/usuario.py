"""Modelo de Usuario: cuenta de acceso a la aplicación.

Separado de Personal a propósito: no todo el personal de la empresa
necesita poder entrar al sistema (hoy solo IT), y una cuenta de acceso
no siempre corresponde a alguien del directorio (p. ej. una cuenta de
servicio). Por eso el vínculo con Personal es opcional.

Hereda de UserMixin (Flask-Login) para exponer is_authenticated,
is_active, is_anonymous y get_id() sin tener que reimplementarlos.
"""
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import Base, generar_uuid


class Usuario(Base, UserMixin):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generar_uuid)
    username: Mapped[str] = mapped_column(String(45), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    id_personal: Mapped[str | None] = mapped_column(String(36), ForeignKey("personal.id"))
    personal: Mapped["Personal"] = relationship()

    def set_password(self, password_en_claro: str) -> None:
        self.password_hash = generate_password_hash(password_en_claro)

    def check_password(self, password_en_claro: str) -> bool:
        return check_password_hash(self.password_hash, password_en_claro)

    def __repr__(self) -> str:
        return f"<Usuario {self.username}>"
