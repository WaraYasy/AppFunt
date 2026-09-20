"""Modelo de assets (equipo tecnológico) de la empresa."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, generar_uuid


class AssetCategoria:
    """Categorías disponibles para clasificar un asset."""

    PORTATIL = "Portátil"
    SOBREMESA = "Sobremesa"
    SERVIDOR = "Servidor"
    REDES = "Redes"
    MOVIL = "Móvil"
    PERIFERICO = "Periférico"
    OTRO = "Otro"

    OPCIONES = [PORTATIL, SOBREMESA, SERVIDOR, REDES, MOVIL, PERIFERICO, OTRO]


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generar_uuid)
    codigo: Mapped[str | None] = mapped_column(String(6), unique=True, index=True)
    id_personal: Mapped[str | None] = mapped_column(String(36), ForeignKey("personal.id"))
    nombre: Mapped[str] = mapped_column(String(100))
    categoria: Mapped[str] = mapped_column(String(20), default=AssetCategoria.OTRO)
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    estado: Mapped[str] = mapped_column(String(20), default="Disponible")

    # Ficha técnica ampliada (opcional: no todos los activos la tienen completa)
    numero_serie: Mapped[str | None] = mapped_column(String(60), unique=True, index=True)
    cpu: Mapped[str | None] = mapped_column(String(120))
    ram: Mapped[str | None] = mapped_column(String(60))
    almacenamiento: Mapped[str | None] = mapped_column(String(120))
    sistema_operativo: Mapped[str | None] = mapped_column(String(80))
    garantia: Mapped[str | None] = mapped_column(String(120))

    custodio: Mapped["Personal"] = relationship(back_populates="assets")

    def __repr__(self) -> str:
        return f"<Asset {self.nombre} ({self.categoria})>"
