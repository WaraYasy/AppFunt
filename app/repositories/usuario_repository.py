"""Repositorio de acceso a datos para Usuario (cuentas de acceso)."""
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class UsuarioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.username == username).first()

    def get_by_personal(self, id_personal: str) -> Usuario | None:
        return self.db.query(Usuario).filter(Usuario.id_personal == id_personal).first()

    def ids_personal_con_cuenta(self) -> set[str]:
        """ids de Personal que tienen una cuenta de acceso vinculada, en una
        sola consulta (para no hacer N+1 al serializar el listado completo)."""
        filas = self.db.query(Usuario.id_personal).filter(Usuario.id_personal.isnot(None)).all()
        return {id_personal for (id_personal,) in filas}
