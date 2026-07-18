from fastapi import HTTPException
from sqlalchemy import String, cast, desc, or_, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.exceptions import TransaccionValidationError
from app.modules.comercial.turnos import model_turno
from . import model_cierreturno, schema_cierreturno

MAX_LOGS_AUDITORIA = 10


def _limitar_logs(logs):
    return logs[-MAX_LOGS_AUDITORIA:] if logs else logs


def get_cierres_paginated(db: Session, page: int, size: int, idempresa: int, texto: str = None):
    query = db.query(model_cierreturno.TCierreTurno).filter(
        model_cierreturno.TCierreTurno.id_emp == idempresa
    )

    if texto:
        patron = f"%{texto}%"
        query = query.join(model_cierreturno.TCierreTurno.turno).filter(
            or_(
                cast(model_cierreturno.TCierreTurno.id_trans, String).ilike(patron),
                model_turno.TAbrirTurno.usuario.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query.options(
        joinedload(model_cierreturno.TCierreTurno.turno).joinedload(model_turno.TAbrirTurno.caja)
    ).order_by(desc(model_cierreturno.TCierreTurno.fecha_cierre)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


# Resumen agrupado de td_abrirturno para el turno - lo que el formulario de cierre
# usa para pre-llenar la grilla (importe_sistema por concepto/medio de pago/signo)
# antes de que el usuario ingrese lo realmente contado.
def get_resumen_cierre(db: Session, id_turno: int):
    turno = db.query(model_turno.TAbrirTurno).filter(
        model_turno.TAbrirTurno.id == id_turno
    ).options(joinedload(model_turno.TAbrirTurno.caja)).first()

    if not turno:
        raise HTTPException(status_code=404, detail="Turno no encontrado")
    if not turno.status:
        raise HTTPException(status_code=400, detail="Este turno ya esta cerrado")

    query = text("""
        SELECT ta.concepto, ta.id_mediopago, mp.tipo AS nombre_mediopago, ta.signo,
               SUM(ta.importe) AS importe_sistema
        FROM td_abrirturno ta
        JOIN m_mediopagos mp ON mp.id = ta.id_mediopago
        WHERE ta.id_turno = :id_turno
        GROUP BY ta.concepto, ta.id_mediopago, mp.tipo, ta.signo
        ORDER BY ta.concepto, mp.tipo, ta.signo
    """)
    lineas = db.execute(query, {"id_turno": id_turno}).mappings().all()

    return {
        "id_turno": id_turno,
        "imp_base": turno.imp_base or 0,
        "nom_caja": turno.caja.nom_caja if turno.caja else "",
        "lineas": lineas
    }


# Nivel 2 del drill-down de cierre: facturas individuales detras de una fila
# agrupada de la grilla (mismo concepto/medio de pago/signo). id_referencia en
# td_abrirturno es el id_trans de la venta que origino ese movimiento - con pago
# mixto, una sola venta puede aportar mas de una linea aca (una por medio de
# pago usado), por eso se trae tambien el total real de la factura.
def get_detalle_concepto(db: Session, id_turno: int, concepto: str, id_mediopago: int, signo: int):
    query = text("""
        SELECT ta.fecha, ta.id_referencia AS id_trans, ta.importe,
               (f.serie_docum || CAST(f.nro_docum AS varchar)) AS factura,
               f.imp_total AS importe_total_factura,
               COALESCE(c.nom_cliente, '') AS cliente
        FROM td_abrirturno ta
        JOIN t_facturas f ON f.id_trans = ta.id_referencia
        LEFT JOIN m_clientes c ON c.id_cliente = f.id_cliente
        WHERE ta.id_turno = :id_turno AND ta.concepto = :concepto
          AND ta.id_mediopago = :id_mediopago AND ta.signo = :signo
        ORDER BY ta.fecha
    """)
    return db.execute(query, {
        "id_turno": id_turno,
        "concepto": concepto,
        "id_mediopago": id_mediopago,
        "signo": signo
    }).mappings().all()


def get_cierre_by_id(db: Session, id: int):
    return db.query(model_cierreturno.TCierreTurno).filter(
        model_cierreturno.TCierreTurno.id_trans == id
    ).options(
        joinedload(model_cierreturno.TCierreTurno.detalles).joinedload(model_cierreturno.TDCierreTurno.mediopago),
        joinedload(model_cierreturno.TCierreTurno.turno).joinedload(model_turno.TAbrirTurno.caja)
    ).first()


# Crea el cierre (cabecera + detalle agrupado, ya calculado por el frontend/llamador
# a partir de get_resumen_cierre - este repositorio no vuelve a agrupar td_abrirturno)
# y llama sp_comercial_cierreturno, que traslada el dinero a p_movimientocajas y
# marca el turno como cerrado (t_abrirturno.status = false).
def create_cierre(db: Session, obj: schema_cierreturno.CierreTurnoCreate):
    try:
        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])

        db_cierre = model_cierreturno.TCierreTurno(
            id_emp=obj.id_emp,
            id_turno=obj.id_turno,
            fecha_cierre=obj.fecha_cierre,
            observacion=obj.observacion,
            imp_base=obj.imp_base,
            imp_total=obj.imp_total,
            descuadre=obj.descuadre,
            imp_descuadre=obj.imp_descuadre,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(db_cierre)
        db.flush()

        for i, det in enumerate(obj.detalles, start=1):
            db.add(model_cierreturno.TDCierreTurno(
                id_cierre=db_cierre.id_trans,
                linea=i,
                concepto=det.concepto,
                id_mediopago=det.id_mediopago,
                signo=det.signo,
                importe_sistema=det.importe_sistema,
                valor_usuario=det.valor_usuario,
                diferencia=det.diferencia
            ))
        db.flush()

        db.execute(
            text("CALL public.sp_comercial_cierreturno(:operacion, :parm_cierre)"),
            {"operacion": "N", "parm_cierre": db_cierre.id_trans}
        )

        db.commit()
        db.refresh(db_cierre)
        return db_cierre

    except (IntegrityError, DataError):
        # No se envuelve: el manejador global responde con el mensaje amigable
        # especifico (ej. UNIQUE(id_turno) violado si el turno ya estaba cerrado).
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise TransaccionValidationError(str(e.orig))
