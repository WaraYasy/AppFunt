"""Repositorio de acceso a datos para assets (equipo tecnológico)."""
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.assets import Asset


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Asset]:
        """Devuelve todos los assets, con su custodio cargado, del más reciente al más antiguo."""
        return (
            self.db.query(Asset)
            .options(joinedload(Asset.custodio))
            .order_by(Asset.created.desc())
            .all()
        )

    def get_all_by_personal(self, id_personal: str) -> list[Asset]:
        return self.db.query(Asset).filter(Asset.id_personal == id_personal).all()

    def count_all(self) -> int:
        return self.db.query(func.count(Asset.id)).scalar()

    def count_by_categoria(self) -> list[tuple[str, int]]:
        """Devuelve el total de assets agrupado por categoría."""
        return (
            self.db.query(Asset.categoria, func.count(Asset.id))
            .group_by(Asset.categoria)
            .all()
        )

    def count_disponibles(self) -> int:
        return (
            self.db.query(func.count(Asset.id))
            .filter(Asset.estado == "Disponible")
            .scalar()
        )

    def count_asignados(self) -> int:
        return (
            self.db.query(func.count(Asset.id))
            .filter(Asset.id_personal.isnot(None))
            .scalar()
        )

    def get_recientes(self, limite: int = 4) -> list[Asset]:
        """Devuelve los assets más recientemente creados, con su custodio cargado."""
        return (
            self.db.query(Asset)
            .options(joinedload(Asset.custodio))
            .order_by(Asset.created.desc())
            .limit(limite)
            .all()
        )
