from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_motivodevolucionventa, schema_motivodevolucionventa
from app.core.numeradores import repository_numerador

MAX_LOGS_AUDITORIA = 10
CODIGO_NUMERADOR_MOTIVODEVOLUCIONVENTA = "MOTIVODEVOLUCIONVENTA"


def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def _obtener_cod_motivo(db: Session, id_emp: int, cod_motivo_manual):
    """Asigna el codMotivo desde el numerador de la empresa (2 digitos). Si la
    empresa tiene "requiere_consecutivo" en False, respeta lo enviado desde el
    formulario (modo manual) - mismo criterio que motivosdevolucion (Compras)."""
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_MOTIVODEVOLUCIONVENTA)
    if siguiente is None:
        return cod_motivo_manual
    return repository_numerador.formatear_numerador(siguiente, longitud=2)


def get_all(db: Session, id_emp: int):
    return db.query(model_motivodevolucionventa.MotivoDevolucionVenta) \
        .filter(model_motivodevolucionventa.MotivoDevolucionVenta.id_emp == id_emp) \
        .all()


def get_motivo(db: Session, id_motivo: int):
    return db.query(model_motivodevolucionventa.MotivoDevolucionVenta).filter(
        model_motivodevolucionventa.MotivoDevolucionVenta.id == id_motivo).first()


def create_motivo(db: Session, obj: schema_motivodevolucionventa.MotivoDevolucionVentaCreate):
    data = obj.model_dump()
    data["logs"] = _limitar_logs(data.get("logs"))
    data["cod_motivo"] = _obtener_cod_motivo(db, data["id_emp"], data.get("cod_motivo"))
    db_motivo = model_motivodevolucionventa.MotivoDevolucionVenta(**data)

    db.add(db_motivo)
    db.commit()
    db.refresh(db_motivo)
    return db_motivo


def update_motivo(db: Session, id_motivo: int, obj: schema_motivodevolucionventa.MotivoDevolucionVentaCreate):
    db_query = db.query(model_motivodevolucionventa.MotivoDevolucionVenta).filter(
        model_motivodevolucionventa.MotivoDevolucionVenta.id == id_motivo)
    db_motivo = db_query.first()

    if db_motivo:
        update_data = obj.model_dump()
        update_data["logs"] = _limitar_logs(update_data.get("logs"))
        db_query.update(update_data, synchronize_session=False)
        db.commit()
        db.refresh(db_motivo)
    return db_motivo


def delete_motivo(db: Session, id_motivo: int):
    db_motivo = db.query(model_motivodevolucionventa.MotivoDevolucionVenta).filter(
        model_motivodevolucionventa.MotivoDevolucionVenta.id == id_motivo).first()
    if db_motivo:
        db.delete(db_motivo)
        db.commit()
    return db_motivo


def get_motivos_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_motivodevolucionventa.MotivoDevolucionVenta) \
        .filter(model_motivodevolucionventa.MotivoDevolucionVenta.id_emp == id_emp)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_motivodevolucionventa.MotivoDevolucionVenta.cod_motivo.ilike(patron),
                model_motivodevolucionventa.MotivoDevolucionVenta.nom_motivo.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query.order_by(desc(model_motivodevolucionventa.MotivoDevolucionVenta.fecha_mod)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
