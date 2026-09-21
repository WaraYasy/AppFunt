"""Data access repository for assets (tech equipment)."""
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import generar_codigo
from app.models.assets import Asset


class AssetRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **campos) -> Asset:
        """Create and save an Asset. Auto-generates `codigo` if it's not in `campos`."""
        campos.setdefault("codigo", generar_codigo(self.db, Asset.codigo, prefijo="NX-"))
        asset = Asset(**campos)
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def update(self, asset: Asset, **campos) -> Asset:
        """Update only the editable fields of an existing Asset."""
        for campo, valor in campos.items():
            setattr(asset, campo, valor)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def delete(self, asset: Asset) -> None:
        """Delete an Asset. It has no dependents (nothing references an Asset)."""
        self.db.delete(asset)
        self.db.commit()

    def get_by_id(self, id_asset: str) -> Asset | None:
        return (
            self.db.query(Asset)
            .options(joinedload(Asset.custodio))
            .filter(Asset.id == id_asset)
            .first()
        )

    def existe_numero_serie(self, numero_serie: str, excluir_id: str | None = None) -> bool:
        """Check if `numero_serie` is already used by another asset.

        `excluir_id` skips a given asset, so editing it doesn't flag its
        own serial number as a duplicate.
        """
        query = self.db.query(Asset.id).filter(Asset.numero_serie == numero_serie)
        if excluir_id:
            query = query.filter(Asset.id != excluir_id)
        return query.first() is not None

    def get_all(self) -> list[Asset]:
        """Return every asset, with its custodian loaded, newest first."""
        return (
            self.db.query(Asset)
            .options(joinedload(Asset.custodio))
            .order_by(Asset.created.desc())
            .all()
        )

    def get_all_by_persona(self, id_persona: str) -> list[Asset]:
        return self.db.query(Asset).filter(Asset.id_persona == id_persona).all()

    def count_all(self) -> int:
        return self.db.query(func.count(Asset.id)).scalar()

    def count_by_categoria(self) -> list[tuple[str, int]]:
        """Return the asset count grouped by category."""
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
            .filter(Asset.id_persona.isnot(None))
            .scalar()
        )

    def get_recientes(self, limite: int = 4) -> list[Asset]:
        """Return the most recently created assets, with their custodian loaded."""
        return (
            self.db.query(Asset)
            .options(joinedload(Asset.custodio))
            .order_by(Asset.created.desc())
            .limit(limite)
            .all()
        )
