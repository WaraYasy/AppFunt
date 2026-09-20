"""Modelo de Persona: directorio de empleados de la empresa.

Persona es una entidad de negocio (quién es cada empleado, en qué
departamento está, de qué activos es custodio) separada a propósito de
Admin (la cuenta con la que se inicia sesión en la aplicación) — ver
app/models/admin.py.
"""
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.database import Base, generar_uuid
from app.validacion import validar_email, validar_longitud, validar_no_vacio, validar_opciones


class PersonaModalidad:
    """Modalidad de trabajo del colaborador."""

    REMOTO = "Remoto"
    PRESENCIAL = "Presencial"

    OPCIONES = [REMOTO, PRESENCIAL]


class PersonaDepartamento:
    """Departamentos válidos — lista cerrada."""

    INGENIERIA = "Ingeniería"
    DISENO = "Diseño"
    PRODUCTO = "Producto"
    VENTAS = "Ventas"
    RRHH = "RRHH"
    ADMINISTRACION = "Administración"
    IT = "IT"

    OPCIONES = [INGENIERIA, DISENO, PRODUCTO, VENTAS, RRHH, ADMINISTRACION, IT]


class PersonaUbicacion:
    """Sedes válidas — lista cerrada."""

    CENTRAL = "Central"
    SUCURSAL_1 = "Sucursal 1"

    OPCIONES = [CENTRAL, SUCURSAL_1]


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generar_uuid)
    nombre: Mapped[str] = mapped_column(String(45))
    apellido: Mapped[str] = mapped_column(String(45))
    created: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # Identificación y contacto (opcionales: no todo el personal legado los tiene cargados)
    email: Mapped[str | None] = mapped_column(String(120), unique=True)
    codigo: Mapped[str | None] = mapped_column(String(10), unique=True, index=True)

    # Datos organizativos (opcionales, usados en la ficha de activo asignado)
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
