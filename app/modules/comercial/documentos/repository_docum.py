from fastapi import HTTPException
from sqlalchemy import desc, func, text
from sqlalchemy.orm import Session , joinedload
from . import model_docum, schema_docum


def consulta_x_documento(db: Session, id_emp: int, id_sucursal: int, documento: str):
    return db.query(model_docum.DocumentoVenta).filter(
        model_docum.DocumentoVenta.id_emp == id_emp,
        model_docum.DocumentoVenta.id_sucursal_emp == id_sucursal,
        func.lower(model_docum.DocumentoVenta.documento) == documento.lower()
    ).first()