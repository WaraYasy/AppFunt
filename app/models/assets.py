"""Modelo de assets (equipo tecnológico) de la empresa."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AssetCategoria:
    """Categorías disponibles para clasificar un asset."""

    PORTATIL = "Portátil"
    SOBREMESA = "Sobremesa"
    MONITOR = "Monitor"
    TECLADO = "Teclado"
    RATON = "Ratón"
    MOVIL = "Móvil"
    IMPRESORA = "Impresora"
    OTRO = "Otro"

    OPCIONES = [PORTATIL, SOBREMESA, MONITOR, TECLADO, RATON, MOVIL, IMPRESORA, OTRO]


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    codigo: Mapped[str | None] = mapped_column(String(6), unique=True, index=True)
    id_user: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    categoria: Mapped[str] = mapped_column(String(20), default=AssetCategoria.OTRO)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    estado: Mapped[str] = mapped_column(String(20), default="Disponible")

    usuario: Mapped["Users"] = relationship(back_populates="assets")

    def __repr__(self) -> str:
        return f"<Asset {self.nombre} ({self.categoria})>"
