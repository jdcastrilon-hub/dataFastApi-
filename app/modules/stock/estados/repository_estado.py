from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_estado, schema_estado
from app.core.numeradores import repository_numerador

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

# Codigo del numerador (por empresa) que identifica el consecutivo de cod_estado
CODIGO_NUMERADOR_ESTADO = "ESTADO"

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

def _obtener_cod_estado(db: Session, id_emp: int, cod_estado_manual):
    """
    Asigna el codEstado desde el numerador de la empresa (2 digitos, ver
    docs/tecnica/specs/core/autonumeracion-catalogos.md). Si la empresa tiene
    "requiere_consecutivo" en False, respeta lo que haya enviado el formulario
    (modo manual) - mismo criterio que _obtener_cod_articulo/_obtener_cod_bodega.
    """
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_ESTADO)
    if siguiente is None:
        return cod_estado_manual

    return repository_numerador.formatear_numerador(siguiente, longitud=2)

# Obtener todos los estados de la empresa (usado por el combo)
def get_estados(db: Session, id_emp: int):
    return db.query(model_estado.Estado).filter(model_estado.Estado.id_emp == id_emp , model_estado.Estado.activo==True).all()

# Obtener un estado por ID
def get_estado(db: Session, estado_id: int):
    return db.query(model_estado.Estado).filter(model_estado.Estado.id == estado_id).first()

# Crear un estado
def create_estado(db: Session, obj: schema_estado.EstadoCreate):
    data = obj.model_dump()
    data["logs"] = _limitar_logs(data.get("logs"))
    data["cod_estado"] = _obtener_cod_estado(db, data["id_emp"], data.get("cod_estado"))
    db_estado = model_estado.Estado(**data)

    db.add(db_estado)
    db.commit()
    db.refresh(db_estado) # Aquí se recupera el ID generado por el autonumérico
    return db_estado

# Actualizar estado
def update_estado(db: Session, estado_id: int, obj: schema_estado.EstadoCreate):
    db_query = db.query(model_estado.Estado).filter(model_estado.Estado.id == estado_id)
    db_estado = db_query.first()

    if db_estado:
        update_data = obj.model_dump()
        update_data["logs"] = _limitar_logs(update_data.get("logs"))
        db_query.update(update_data, synchronize_session=False)
        db.commit()
        db.refresh(db_estado)
    return db_estado

# Eliminar estado
def delete_estado(db: Session, estado_id: int):
    db_estado = db.query(model_estado.Estado).filter(model_estado.Estado.id == estado_id).first()
    if db_estado:
        db.delete(db_estado)
        db.commit()
    return db_estado

#Paginacion
def get_estados_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_estado.Estado).filter(model_estado.Estado.id_emp == id_emp)

    # Filtro de busqueda por codigo o nombre (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_estado.Estado.cod_estado.ilike(patron),
                model_estado.Estado.nom_estado.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query.order_by(desc(model_estado.Estado.fecha_mod)).offset(offset).limit(size).all()

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
