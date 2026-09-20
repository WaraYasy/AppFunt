"""Configuración de la base de datos con SQLAlchemy 2.0.

Define el engine, la fábrica de sesiones y la clase Base de la que
heredan todos los modelos.
"""
import random
import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, scoped_session, sessionmaker

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


def generar_codigo(db: Session, columna, prefijo: str, digitos: int = 4) -> str:
    """Genera un código corto único (ej. 'NX-8821') para una columna con constraint unique.

    `columna` es el atributo de clase mapeado (ej. Asset.codigo). Reintenta con
    un nuevo sufijo aleatorio si hay colisión; con `digitos=4` el espacio de
    valores (10 000 combinaciones) hace la colisión muy poco probable.
    """
    for _ in range(20):
        sufijo = str(random.randint(0, 10**digitos - 1)).zfill(digitos)
        candidato = f"{prefijo}{sufijo}"
        ya_existe = db.query(columna).filter(columna == candidato).first() is not None
        if not ya_existe:
            return candidato
    raise RuntimeError(f"No se pudo generar un código único con prefijo {prefijo!r}")
