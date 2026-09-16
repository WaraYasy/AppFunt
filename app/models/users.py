"""_summary_

"""
from datetime import datetime

from sqlalchemy import Column, DateTime, String

from app.database import Base

class Users(Base):
    """_summary_

    Args:
        Base (_type_): _description_
    """
    
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, nullable=False)
    username = Column(String(45), unique=True, nullable=False)
    nombre = Column(String(45), nullable=False)
    apellido = Column(String(45), nullable=False)
    password = Column(String(255), nullable=False)
    created = Column(DateTime, default=datetime.now, nullable=False)    