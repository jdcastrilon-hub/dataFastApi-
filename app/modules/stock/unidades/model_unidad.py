from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import relationship

class Unidad(Base):
    __tablename__ = "m_unidades"
    __table_args__ = (
        UniqueConstraint('cod_unidad', name='m_unidades_pk_unica'),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    cod_unidad = Column(String(10), nullable=False)
    nom_unidad = Column(String(50), nullable=False)
    es_paquete = Column(String(2), nullable=False) # 'SI' / 'NO'
    convuni = Column(Integer, nullable=False)
    
    # Usamos JSONB porque es más eficiente para búsquedas en PostgreSQL
    logs = Column(JSONB, nullable=True)
    
    # fecha_mod es de tipo Date en tu SQL, lo mapeamos así:
    fecha_mod = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Relación hacia Artículos (Opcional, pero útil si quieres ver qué artículos usan esta unidad)
    articulos = relationship("Articulo", back_populates="unidad")

    def __repr__(self):
        return f"<Unidad(cod='{self.cod_unidad}', nombre='{self.nom_unidad}')>"