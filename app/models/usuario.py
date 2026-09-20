"""Modelo de Usuario: cuenta de acceso a la aplicación.

Separado de Personal a propósito: no todo el personal de la empresa
necesita poder entrar al sistema (hoy solo IT), y una cuenta de acceso
no siempre corresponde a alguien del directorio (p. ej. una cuenta de
servicio). Por eso el vínculo con Personal es opcional.
"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generar_uuid


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generar_uuid)
    username: Mapped[str] = mapped_column(String(45), unique=True)
    password: Mapped[str] = mapped_column(String(255))
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    id_personal: Mapped[str | None] = mapped_column(String(36), ForeignKey("personal.id"))
    personal: Mapped["Personal"] = relationship()

    def __repr__(self) -> str:
        return f"<Usuario {self.username}>"
