"""Repositorio de acceso a datos para Persona (directorio de empleados)."""
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.database import generar_codigo
from app.models.assets import Asset
from app.models.persona import Persona


class PersonaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **campos) -> Persona:
        """Crea y persiste una Persona. `codigo` se autogenera si no viene en `campos`."""
        campos.setdefault("codigo", generar_codigo(self.db, Persona.codigo, prefijo="EMP-"))
        persona = Persona(**campos)
        self.db.add(persona)
        self.db.commit()
        self.db.refresh(persona)
        return persona

    def update(self, persona: Persona, **campos) -> Persona:
        """Actualiza únicamente los campos editables de una Persona ya existente."""
        for campo, valor in campos.items():
            setattr(persona, campo, valor)
        self.db.commit()
        self.db.refresh(persona)
        return persona

    def delete(self, persona: Persona) -> int:
        """Elimina una Persona. Sus assets no se borran: quedan sin custodio
        (id_persona=NULL). Devuelve cuántos activos quedaron así."""
        activos_asignados = self.db.query(Asset).filter(Asset.id_persona == persona.id).all()
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
        query = self.db.query(Persona.id).filter(Persona.email == email)
        if excluir_id:
            query = query.filter(Persona.id != excluir_id)
        return query.first() is not None

    def get_all(self) -> list[Persona]:
        """Devuelve todo el personal, con sus assets cargados, ordenado por nombre."""
        return (
            self.db.query(Persona)
            .options(selectinload(Persona.assets))
            .order_by(Persona.nombre, Persona.apellido)
            .all()
        )

    def count_all(self) -> int:
        return self.db.query(func.count(Persona.id)).scalar()

    def count_by_modalidad(self) -> list[tuple[str, int]]:
        """Devuelve el total de personal agrupado por modalidad de trabajo."""
        return (
            self.db.query(Persona.modalidad, func.count(Persona.id))
            .group_by(Persona.modalidad)
            .all()
        )
