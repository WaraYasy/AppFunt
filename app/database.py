"""Configuración de la base de datos con SQLAlchemy 2.0.

Define el engine, la fábrica de sesiones y la clase Base de la que
heredan todos los modelos.
"""
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, scoped_session, sessionmaker

from app.config import Config

is_sqlite = Config.SQLALCHEMY_DATABASE_URI.startswith("sqlite")

engine = create_engine(
    Config.SQLALCHEMY_DATABASE_URI,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    echo=False,
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


class Base(DeclarativeBase):
    pass


def generar_uuid() -> str:
    """Genera un identificador único (UUID4) como string de 36 caracteres.

    Se usa como valor por defecto de la PK en los modelos, para no depender
    de que quien crea el objeto recuerde asignar un id único a mano.
    """
    return str(uuid.uuid4())
