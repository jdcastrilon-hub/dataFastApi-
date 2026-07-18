from fastapi import HTTPException
from sqlalchemy import desc, func, or_, text
from sqlalchemy.orm import Session , joinedload
from . import model_docum, schema_docum

MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs: list) -> list:
    return logs[-MAX_LOGS_AUDITORIA:] if logs else logs


def consulta_x_documento(db: Session, id_emp: int, id_sucursal: int, documento: str):
    return db.query(model_docum.DocumentoVenta).filter(
        model_docum.DocumentoVenta.id_emp == id_emp,
        model_docum.DocumentoVenta.id_sucursal_emp == id_sucursal,
        func.lower(model_docum.DocumentoVenta.documento) == documento.lower()
    ).first()

#Paginacion
def get_documentos_paginated(db: Session, page: int, size: int, idempresa: int, texto: str = None):
    query = db.query(model_docum.DocumentoVenta).filter(model_docum.DocumentoVenta.id_emp == idempresa)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_docum.DocumentoVenta.documento.ilike(patron),
                model_docum.DocumentoVenta.descripcion.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query\
        .options(joinedload(model_docum.DocumentoVenta.sucursal))\
        .order_by(desc(model_docum.DocumentoVenta.fecha_mod))\
        .offset(offset)\
        .limit(size)\
        .all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

# Obtener un documento de venta por su llave compuesta
def get_documento_by_key(db: Session, id_emp: int, id_sucursal_emp: int, documento: str):
    return db.query(model_docum.DocumentoVenta).filter(
        model_docum.DocumentoVenta.id_emp == id_emp,
        model_docum.DocumentoVenta.id_sucursal_emp == id_sucursal_emp,
        model_docum.DocumentoVenta.documento == documento
    ).options(joinedload(model_docum.DocumentoVenta.sucursal)).first()

# Crear un documento de venta
def create_documento(db: Session, obj: schema_docum.MDocumVentasCreate):
    db_documento = model_docum.DocumentoVenta(
        id_emp=obj.id_emp,
        id_sucursal_emp=obj.id_sucursal_emp,
        documento=obj.documento,
        descripcion=obj.descripcion,
        serie_docum=obj.serie_docum,
        clase_docum=obj.clase_docum,
        secuencia=obj.secuencia,
        aplica_pos=obj.aplica_pos,
        activo=obj.activo,
        logs=_limitar_logs([log.model_dump() for log in obj.logs] if obj.logs else []),
        fecha_mod=obj.fecha_mod
    )
    db.add(db_documento)
    db.commit()
    db.refresh(db_documento)
    return db_documento

# Actualizar un documento de venta. id_emp/id_sucursal_emp/documento originales
# identifican la fila (llave compuesta); obj trae los valores nuevos, que pueden
# incluir un "documento" (codigo) distinto - SQLAlchemy actualiza la PK sin problema
# via UPDATE ... SET documento=nuevo WHERE ... documento=original.
def update_documento(db: Session, id_emp: int, id_sucursal_emp: int, documento: str, obj: schema_docum.MDocumVentasCreate):
    db_documento = db.query(model_docum.DocumentoVenta).filter(
        model_docum.DocumentoVenta.id_emp == id_emp,
        model_docum.DocumentoVenta.id_sucursal_emp == id_sucursal_emp,
        model_docum.DocumentoVenta.documento == documento
    ).first()
    if not db_documento:
        return None

    db_documento.id_sucursal_emp = obj.id_sucursal_emp
    db_documento.documento = obj.documento
    db_documento.descripcion = obj.descripcion
    db_documento.serie_docum = obj.serie_docum
    db_documento.clase_docum = obj.clase_docum
    db_documento.secuencia = obj.secuencia
    db_documento.aplica_pos = obj.aplica_pos
    db_documento.activo = obj.activo
    db_documento.logs = _limitar_logs([log.model_dump() for log in obj.logs] if obj.logs else [])
    db_documento.fecha_mod = obj.fecha_mod

    db.commit()
    db.refresh(db_documento)
    return db_documento

# Eliminar un documento de venta
def delete_documento(db: Session, id_emp: int, id_sucursal_emp: int, documento: str):
    db_documento = db.query(model_docum.DocumentoVenta).filter(
        model_docum.DocumentoVenta.id_emp == id_emp,
        model_docum.DocumentoVenta.id_sucursal_emp == id_sucursal_emp,
        model_docum.DocumentoVenta.documento == documento
    ).first()
    if not db_documento:
        return None

    db.delete(db_documento)
    db.commit()
    return db_documento
