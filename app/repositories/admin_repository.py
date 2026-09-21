"""Data access repository for Admin (login accounts)."""
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
        """Return ids of every Persona with a linked login account.

        Runs as a single query, so serializing the full Persona list
        doesn't trigger an N+1.
        """
        filas = self.db.query(Admin.id_persona).filter(Admin.id_persona.isnot(None)).all()
        return {id_persona for (id_persona,) in filas}
