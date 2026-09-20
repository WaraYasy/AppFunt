"""Repositorio de acceso a datos para assets (equipo tecnológico)."""
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models.assets import Asset


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Asset]:
        """Devuelve todos los assets, con su usuario cargado, del más reciente al más antiguo."""
        return (
            self.db.query(Asset)
            .options(joinedload(Asset.usuario))
            .order_by(Asset.created.desc())
            .all()
        )

    def get_all_by_user(self, id_user: str) -> list[Asset]:
        return self.db.query(Asset).filter(Asset.id_user == id_user).all()

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
            .filter(Asset.id_user.isnot(None))
            .scalar()
        )

    def get_recientes(self, limite: int = 4) -> list[Asset]:
        """Devuelve los assets más recientemente creados, con su usuario cargado."""
        return (
            self.db.query(Asset)
            .options(joinedload(Asset.usuario))
            .order_by(Asset.created.desc())
            .limit(limite)
            .all()
        )
