from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class Costeo(Base):
    __tablename__ = "m_costeo"
    __table_args__ = {'schema': 'public'}

    # Definición de columnas según tu script SQL
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_costeo = Column(String(20), nullable=False)
    nombre_costeo = Column(String(50), nullable=False)
    
    # Auditoría
    logs = Column(JSON, nullable=True)
    
    # fecha_mod: mapeado como 'timestamp without time zone'
    # func.now() se encarga de la fecha actual al crear y actualizar
    fecha_mod = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Costeo(tipo='{self.tipo_costeo}', nombre='{self.nombre_costeo}')>"