"""Modelo de empleados de la empresa."""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generar_uuid


class Users(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generar_uuid)
    username: Mapped[str] = mapped_column(String(45), unique=True)
    nombre: Mapped[str] = mapped_column(String(45))
    apellido: Mapped[str] = mapped_column(String(45))
    password: Mapped[str] = mapped_column(String(255))
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Datos organizativos (opcionales, usados en la ficha de activo asignado)
    rol: Mapped[str | None] = mapped_column(String(80))
    departamento: Mapped[str | None] = mapped_column(String(80))
    ubicacion: Mapped[str | None] = mapped_column(String(120))

    assets: Mapped[list["Asset"]] = relationship(back_populates="usuario")

    def __repr__(self) -> str:
        return f"<Users {self.username}>"
