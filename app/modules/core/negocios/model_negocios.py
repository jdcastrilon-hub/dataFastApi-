from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Negocio(Base):
    __tablename__ = "m_negocios"
    __table_args__ = (
        UniqueConstraint('id_emp', 'cod_negocio', name='m_negocios_pk_unique'),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True, index=True)
    id_emp = Column(Integer, ForeignKey("public.m_empresa.id_emp"), nullable=False)
    cod_negocio = Column(String(10), nullable=False)
    nom_negocio = Column(String(100), nullable=False)
    
    # Auditoría
    logs = Column(JSON, nullable=True)
    fecha_mod = Column(DateTime, onupdate=func.now(), nullable=True)

    #Relacion de Empresa -> Negocio
    empresa = relationship("Empresa", back_populates="negocios")

    # Relacion de Negocio -> Empresa
    articulo = relationship("Articulo", back_populates="objnegocio")
    
    # Relación hacia los artículos (Hijos)
    # Esto permitirá que desde el negocio puedas ver sus artículos si lo necesitas
    #articulos = relationship("Articulo", back_populates="negocio")
    

    #ToString
    def __repr__(self):
        return f"<Negocio(nom='{self.nom_negocio}', cod='{self.cod_negocio}')>"