from sqlalchemy import Column, Integer, Sequence, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Ciudad(Base):
    __tablename__ = "m_ciudades"
    __table_args__ = {"schema": "public"}

    id_ciudad = Column(Integer, Sequence('m_ciudades_id_ciudad_seq'),primary_key=True, index=True, autoincrement=True)
    
    # Llave foránea hacia la tabla de departamentos
    id_departamento = Column(Integer, ForeignKey("public.m_departamentos.id_departamento"), nullable=False)
    
    cod_ciudad = Column(String(10), nullable=False)
    nom_ciudad = Column(String(50), nullable=False)

    # Relación (Opcional, permite acceder a ciudad.departamento)
    # Asegúrate de que la clase 'Departamento' esté definida
    #departamento = relationship("Departamento", back_populates="ciudades")

    def __repr__(self):
        return f"<Ciudad(nom_ciudad='{self.nom_ciudad}', cod_ciudad='{self.cod_ciudad}')>"