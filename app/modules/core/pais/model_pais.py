from sqlalchemy import Column, Integer, String
from app.database import Base

class model_pais(Base):
    __tablename__ = "m_pais"
    __table_args__ = {"schema": "public"}

    id_pais = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cod_pais = Column(String(10), nullable=False)
    nom_pais = Column(String(50), nullable=False)