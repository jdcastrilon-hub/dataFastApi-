from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Empresa(Base):
    __tablename__ = "m_empresa"
    __table_args__ = {'schema': 'public'}

    # Definición de columnas basadas en tu script SQL
    id_emp = Column(Integer, primary_key=True, autoincrement=True)
    nom_emp = Column(String(50), nullable=False)
    razon_social = Column(String(50), nullable=False)
    cod_doc = Column(String(5), nullable=False)
    nit = Column(String(20), nullable=False)
    direccion = Column(String(50), nullable=False)
    cod_ciudad = Column(Integer, nullable=False)
    telefono = Column(String(15), nullable=False)
    correo = Column(String(50), nullable=False)
    
    # Campo para almacenar la lista de objetos JSON (logs)
    logs = Column(JSON, nullable=True)
    
    # Campo de fecha que se actualiza automáticamente
    fecha_mod = Column(DateTime, onupdate=func.now())

    # Relacion de Negocio -> Empresa
    negocios = relationship("Negocio", back_populates="empresa")
    proveedores = relationship("Compra", back_populates="empresa")

    #ToString
    def __repr__(self):
        return f"<Empresa(nom_emp='{self.nom_emp}', nit='{self.nit}')>"