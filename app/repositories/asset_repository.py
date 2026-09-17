"""Repositorio de acceso a datos para assets (equipo tecnológico)."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.assets import Asset


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Asset]:
        return self.db.query(Asset).all()

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
