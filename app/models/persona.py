"""Persona model: the company's employee directory.

Persona is a business entity (who each employee is, what department
they're in, which assets they're the custodian of), kept separate on
purpose from Admin (the login account) — see app/models/admin.py.
"""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.database import Base, generar_uuid
from app.validacion import validar_email, validar_longitud, validar_no_vacio, validar_opciones


class PersonaModalidad:
    """Work mode of the collaborator."""

    REMOTO = "Remoto"
    PRESENCIAL = "Presencial"

    OPCIONES = [REMOTO, PRESENCIAL]


class PersonaDepartamento:
    """Valid departments — a closed list."""

    INGENIERIA = "Ingeniería"
    DISENO = "Diseño"
    PRODUCTO = "Producto"
    VENTAS = "Ventas"
    RRHH = "RRHH"
    ADMINISTRACION = "Administración"
    IT = "IT"

    OPCIONES = [INGENIERIA, DISENO, PRODUCTO, VENTAS, RRHH, ADMINISTRACION, IT]


class PersonaUbicacion:
    """Valid office locations — a closed list."""

    CENTRAL = "Central"
    SUCURSAL_1 = "Sucursal 1"

    OPCIONES = [CENTRAL, SUCURSAL_1]


class Persona(Base):
    """Represent a company employee and asset custodian."""

    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generar_uuid)
    nombre: Mapped[str] = mapped_column(String(45))
    apellido: Mapped[str] = mapped_column(String(45))
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Identification and contact info (optional: some legacy staff records lack them)
    email: Mapped[str | None] = mapped_column(String(120), unique=True)
    codigo: Mapped[str | None] = mapped_column(String(10), unique=True, index=True)

    # Organizational data (optional, used on the assigned asset's detail view)
    departamento: Mapped[str | None] = mapped_column(String(80))
    ubicacion: Mapped[str | None] = mapped_column(String(120))
    modalidad: Mapped[str | None] = mapped_column(String(20))

    assets: Mapped[list["Asset"]] = relationship(back_populates="custodio")

    @validates("nombre", "apellido")
    def _validar_identidad(self, key, value):
        value = validar_longitud(self, key, value)
        return validar_no_vacio(key, value)

    @validates("email")
    def _validar_email(self, key, value):
        value = validar_longitud(self, key, value)
        return validar_email(key, value)

    @validates("modalidad")
    def _validar_modalidad(self, key, value):
        value = validar_longitud(self, key, value)
        return validar_opciones(key, value, PersonaModalidad.OPCIONES)

    @validates("departamento")
    def _validar_departamento(self, key, value):
        value = validar_longitud(self, key, value)
        return validar_opciones(key, value, PersonaDepartamento.OPCIONES)

    @validates("ubicacion")
    def _validar_ubicacion(self, key, value):
        value = validar_longitud(self, key, value)
        return validar_opciones(key, value, PersonaUbicacion.OPCIONES)

    @validates("codigo")
    def _validar_opcionales(self, key, value):
        return validar_longitud(self, key, value)

    def __repr__(self) -> str:
        return f"<Persona {self.nombre} {self.apellido}>"
