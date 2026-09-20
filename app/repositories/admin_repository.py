"""Repositorio de acceso a datos para Admin (cuentas de acceso)."""
from sqlalchemy.orm import Session

from app.models.admin import Admin


class AdminRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Admin | None:
        return self.db.query(Admin).filter(Admin.username == username).first()

    def get_by_persona(self, id_persona: str) -> Admin | None:
        return self.db.query(Admin).filter(Admin.id_persona == id_persona).first()

    def ids_persona_con_cuenta(self) -> set[str]:
        """ids de Persona que tienen una cuenta de acceso vinculada, en una
        sola consulta (para no hacer N+1 al serializar el listado completo)."""
        filas = self.db.query(Admin.id_persona).filter(Admin.id_persona.isnot(None)).all()
        return {id_persona for (id_persona,) in filas}
