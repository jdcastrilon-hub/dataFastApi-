from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_motivodevolucion, schema_motivodevolucion
from app.core.numeradores import repository_numerador

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

# Codigo del numerador (por empresa) que identifica el consecutivo de cod_motivo
CODIGO_NUMERADOR_MOTIVODEVOLUCION = "MOTIVODEVOLUCION"

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

def _obtener_cod_motivo(db: Session, id_emp: int, cod_motivo_manual):
    """
    Asigna el codMotivo desde el numerador de la empresa (2 digitos, ver
    docs/tecnica/specs/core/autonumeracion-catalogos.md). Si la empresa tiene
    "requiere_consecutivo" en False, respeta lo que haya enviado el formulario
    (modo manual) - mismo criterio que _obtener_cod_articulo/_obtener_cod_bodega.
    """
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_MOTIVODEVOLUCION)
    if siguiente is None:
        return cod_motivo_manual

    return repository_numerador.formatear_numerador(siguiente, longitud=2)

# Lista para combos (filtrada por empresa: cada empresa maneja sus propios motivos)
def get_all(db: Session, id_emp: int):
    return db.query(model_motivodevolucion.MotivoDevolucion)\
        .filter(model_motivodevolucion.MotivoDevolucion.id_emp == id_emp)\
        .all()

# Obtener un motivo por ID
def get_motivo(db: Session, id_motivo: int):
    return db.query(model_motivodevolucion.MotivoDevolucion).filter(model_motivodevolucion.MotivoDevolucion.id == id_motivo).first()

# Crear un motivo
def create_motivo(db: Session, obj: schema_motivodevolucion.MotivoDevolucionCreate):
    data = obj.model_dump()
    data["logs"] = _limitar_logs(data.get("logs"))
    data["cod_motivo"] = _obtener_cod_motivo(db, data["id_emp"], data.get("cod_motivo"))
    db_motivo = model_motivodevolucion.MotivoDevolucion(**data)

    db.add(db_motivo)
    db.commit()
    db.refresh(db_motivo) # Aquí se recupera el ID generado por el autonumérico
    return db_motivo

# Actualizar motivo
def update_motivo(db: Session, id_motivo: int, obj: schema_motivodevolucion.MotivoDevolucionCreate):
    db_query = db.query(model_motivodevolucion.MotivoDevolucion).filter(model_motivodevolucion.MotivoDevolucion.id == id_motivo)
    db_motivo = db_query.first()

    if db_motivo:
        update_data = obj.model_dump()
        update_data["logs"] = _limitar_logs(update_data.get("logs"))
        db_query.update(update_data, synchronize_session=False)
        db.commit()
        db.refresh(db_motivo)
    return db_motivo

# Eliminar motivo
def delete_motivo(db: Session, id_motivo: int):
    db_motivo = db.query(model_motivodevolucion.MotivoDevolucion).filter(model_motivodevolucion.MotivoDevolucion.id == id_motivo).first()
    if db_motivo:
        db.delete(db_motivo)
        db.commit()
    return db_motivo

#Paginacion (filtrada por empresa)
def get_motivos_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_motivodevolucion.MotivoDevolucion)\
        .filter(model_motivodevolucion.MotivoDevolucion.id_emp == id_emp)

    # Filtro de busqueda por codigo o nombre (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_motivodevolucion.MotivoDevolucion.cod_motivo.ilike(patron),
                model_motivodevolucion.MotivoDevolucion.nom_motivo.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query.order_by(desc(model_motivodevolucion.MotivoDevolucion.fecha_mod)).offset(offset).limit(size).all()

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
