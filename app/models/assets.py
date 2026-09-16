"""_summary_

"""
from datetime import datetime

from sqlalchemy import Column, ForeignKey, String

from app.database import Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, nullable=False)
    codigo = Column(String(6), unique=True, nullable=True, index=True)
    id_user = Column(String(36), ForeignKey("user.id"), nullable=False)
    nombre = Column(String(100), nullable=False)
    created = Column(datetime, default=datetime.now, nullable=False)
    estado = Column(String(20), default="Disponible", nullable=False)   