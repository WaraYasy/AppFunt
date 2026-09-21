"""Admin model: a login account for the app.

Kept separate from Persona on purpose: not everyone on staff needs to
log in to the system (today only IT does), and a login account doesn't
always match someone in the directory (e.g. a service account). That's
why the link to Persona is optional.

Inherits from UserMixin (Flask-Login) to expose is_authenticated,
is_active, is_anonymous, and get_id() without reimplementing them.
"""
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from app.database import Base, generar_uuid


class Admin(Base, UserMixin):
    """Represent a login account used to access the app."""

    __tablename__ = "admins"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generar_uuid)
    username: Mapped[str] = mapped_column(String(45), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    id_persona: Mapped[str | None] = mapped_column(String(36), ForeignKey("personas.id"))
    persona: Mapped["Persona"] = relationship()

    def set_password(self, password_en_claro: str) -> None:
        """Hash the given password and store it."""
        self.password_hash = generate_password_hash(password_en_claro)

    def check_password(self, password_en_claro: str) -> bool:
        """Check the given password against the stored hash."""
        return check_password_hash(self.password_hash, password_en_claro)

    def __repr__(self) -> str:
        return f"<Admin {self.username}>"
