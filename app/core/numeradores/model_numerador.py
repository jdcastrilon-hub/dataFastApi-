from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from app.database import Base

class Numerador(Base):
    __tablename__ = "md_numeradores"
    __table_args__ = {'schema': 'public'}

    id_emp = Column(Integer, ForeignKey("public.md_empresas.id_emp"), primary_key=True)
    codigo = Column(String(30), primary_key=True)
    ultimo_valor = Column(Integer, nullable=False, default=0)
    requiere_consecutivo = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<Numerador(emp={self.id_emp}, codigo='{self.codigo}', ultimo={self.ultimo_valor})>"
