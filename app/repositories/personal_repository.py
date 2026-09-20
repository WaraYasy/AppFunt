"""Repositorio de acceso a datos para Personal (directorio de empleados)."""
from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.database import generar_codigo
from app.models.personal import Personal


class PersonalRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **campos) -> Personal:
        """Crea y persiste una Personal. `codigo` se autogenera si no viene en `campos`."""
        campos.setdefault("codigo", generar_codigo(self.db, Personal.codigo, prefijo="EMP-"))
        persona = Personal(**campos)
        self.db.add(persona)
        self.db.commit()
        self.db.refresh(persona)
        return persona

    def existe_email(self, email: str) -> bool:
        return self.db.query(Personal.id).filter(Personal.email == email).first() is not None

    def get_all(self) -> list[Personal]:
        """Devuelve todo el personal, con sus assets cargados, ordenado por nombre."""
        return (
            self.db.query(Personal)
            .options(selectinload(Personal.assets))
            .order_by(Personal.nombre, Personal.apellido)
            .all()
        )

    def count_all(self) -> int:
        return self.db.query(func.count(Personal.id)).scalar()

    def count_by_modalidad(self) -> list[tuple[str, int]]:
        """Devuelve el total de personal agrupado por modalidad de trabajo."""
        return (
            self.db.query(Personal.modalidad, func.count(Personal.id))
            .group_by(Personal.modalidad)
            .all()
        )
