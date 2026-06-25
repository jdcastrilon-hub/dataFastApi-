from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base

class MedioPago(Base):
    __tablename__ = "m_mediopagos"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, nullable=False)
    tipo = Column(String(20), nullable=False)
    orden= Column(Integer, nullable=False)