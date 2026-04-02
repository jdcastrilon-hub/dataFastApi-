from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class TipoServicio(Base):
    __tablename__ = "m_tiposervicio"
    __table_args__ = {'schema': 'public'}

    # Campos basados en el DDL
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_emp = Column(Integer, nullable=False)
    cod_servicio = Column(String(20), nullable=False)
    nom_servicio = Column(String(50), nullable=False)
    
    # Llave foránea hacia m_costeo
    id_costeo = Column(Integer, ForeignKey("public.m_costeo.id"), nullable=True)


    def __repr__(self): 
        return f"<TipoServicio(id={self.id}, nom_servicio='{self.nom_servicio}')>"