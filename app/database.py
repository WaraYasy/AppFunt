"""Database setup with SQLAlchemy 2.0.

Defines the engine, the session factory, and the Base class that every
model inherits from.
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
    """Generate a unique id (UUID4) as a 36-character string.

    Used as the default primary key value in the models, so whoever
    creates an object doesn't have to remember to set a unique id by hand.
    """
    return str(uuid.uuid4())


def generar_codigo(db: Session, columna, prefijo: str, digitos: int = 4) -> str:
    """Generate a short unique code (e.g. 'NX-8821') for a unique column.

    `columna` is the mapped class attribute (e.g. Asset.codigo). Retries with
    a new random suffix on collision; with `digitos=4` the value space
    (10,000 combinations) makes a collision very unlikely.

    Raises RuntimeError if no unique code is found after 20 attempts.
    """
    for _ in range(20):
        sufijo = str(random.randint(0, 10**digitos - 1)).zfill(digitos)
        candidato = f"{prefijo}{sufijo}"
        ya_existe = db.query(columna).filter(columna == candidato).first() is not None
        if not ya_existe:
            return candidato
    raise RuntimeError(f"No se pudo generar un código único con prefijo {prefijo!r}")
