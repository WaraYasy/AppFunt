"""Data access repository for Persona (employee directory)."""

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.database import generar_codigo
from app.models.assets import Asset
from app.models.persona import Persona


class PersonaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **campos) -> Persona:
        """Create and save a Persona. Auto-generates `codigo` if it's not in `campos`."""
        campos.setdefault(
            "codigo", generar_codigo(self.db, Persona.codigo, prefijo="EMP-")
        )
        persona = Persona(**campos)
        self.db.add(persona)
        self.db.commit()
        self.db.refresh(persona)
        return persona

    def update(self, persona: Persona, **campos) -> Persona:
        """Update only the editable fields of an existing Persona."""
        for campo, valor in campos.items():
            setattr(persona, campo, valor)
        self.db.commit()
        self.db.refresh(persona)
        return persona

    def delete(self, persona: Persona) -> int:
        """Delete a Persona.

        Its assets aren't deleted: they're left without a custodian
        (id_persona=NULL). Returns how many assets were left that way.
        """
        activos_asignados = (
            self.db.query(Asset).filter(Asset.id_persona == persona.id).all()
        )
        for asset in activos_asignados:
            asset.id_persona = None
        self.db.delete(persona)
        self.db.commit()
        return len(activos_asignados)

    def get_by_id(self, id_persona: str) -> Persona | None:
        return (
            self.db.query(Persona)
            .options(selectinload(Persona.assets))
            .filter(Persona.id == id_persona)
            .first()
        )

    def existe_email(self, email: str, excluir_id: str | None = None) -> bool:
        """Check if `email` is already used by another Persona.

        `excluir_id` skips a given person, so editing them doesn't flag
        their own email as a duplicate.
        """
        query = self.db.query(Persona.id).filter(Persona.email == email)
        if excluir_id:
            query = query.filter(Persona.id != excluir_id)
        return query.first() is not None

    def get_all(self) -> list[Persona]:
        """Return every Persona, with their assets loaded, sorted by name."""
        return (
            self.db.query(Persona)
            .options(selectinload(Persona.assets))
            .order_by(Persona.nombre, Persona.apellido)
            .all()
        )

    def count_all(self) -> int:
        return self.db.query(func.count(Persona.id)).scalar()

    def count_by_modalidad(self) -> list[tuple[str, int]]:
        """Return the headcount grouped by work mode."""
        return (
            self.db.query(Persona.modalidad, func.count(Persona.id))
            .group_by(Persona.modalidad)
            .all()
        )
