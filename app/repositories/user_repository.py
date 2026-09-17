"""Repositorio de acceso a datos para empleados."""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.users import Users


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Users]:
        return self.db.query(Users).all()

    def count_all(self) -> int:
        return self.db.query(func.count(Users.id)).scalar()
