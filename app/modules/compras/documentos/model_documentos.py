from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base
from sqlalchemy.orm import relationship

class TipoDocumento(Base):
    __tablename__ = "m_tipodocumentos"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    cod_tipodoc = Column(String(5), nullable=False)
    nom_tipodoc = Column(String(50), nullable=False)
    # Genera la fecha automáticamente al insertar
    fecha_mod = Column(DateTime, nullable=False)

    personas = relationship("Persona", back_populates="tipo_documento")