from fastapi import HTTPException
from sqlalchemy import desc, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.exceptions import TransaccionValidationError
from app.modules.comercial.turnos import model_turno
from app.modules.comercial.cajas import model_cajas
from app.modules.tesoreria.conceptos import model_conceptos
from . import model_movcaja, schema_movcaja

MAX_LOGS_AUDITORIA = 10


def _limitar_logs(logs: list) -> list:
    return logs[-MAX_LOGS_AUDITORIA:] if logs else logs


def get_movcajas_paginated(db: Session, page: int, size: int, idempresa: int, texto: str = None):
    query = db.query(model_movcaja.TMovCaja)\
        .join(model_movcaja.TMovCaja.turno)\
        .join(model_turno.TAbrirTurno.caja)\
        .filter(model_cajas.MCaja.id_emp == idempresa)

    if texto:
        patron = f"%{texto}%"
        query = query.join(model_movcaja.TMovCaja.concepto).filter(
            model_conceptos.MConceptoCaja.nom_concepto.ilike(patron)
        )

    total_records = query.count()

    offset = page * size
    items = query\
        .options(joinedload(model_movcaja.TMovCaja.concepto))\
        .order_by(desc(model_movcaja.TMovCaja.fecha_mod))\
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


def get_movcaja_by_id(db: Session, id: int):
    return db.query(model_movcaja.TMovCaja).filter(model_movcaja.TMovCaja.id == id).options(
        joinedload(model_movcaja.TMovCaja.concepto)
    ).first()


def create_movcaja(db: Session, obj: schema_movcaja.MovCajaCreate):
    try:
        concepto = db.query(model_conceptos.MConceptoCaja).filter(
            model_conceptos.MConceptoCaja.id == obj.id_concepto
        ).first()
        if not concepto:
            raise HTTPException(status_code=404, detail="Concepto no encontrado")
        if not concepto.status:
            raise HTTPException(status_code=400, detail="Este concepto esta inactivo")
        if concepto.aplica_limit and concepto.imp_limit is not None and obj.importe > concepto.imp_limit:
            raise HTTPException(
                status_code=400,
                detail=f"El importe supera el limite de este concepto (maximo ${concepto.imp_limit})."
            )

        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])

        db_mov = model_movcaja.TMovCaja(
            id_concepto=obj.id_concepto,
            id_turno=obj.id_turno,
            fecha=obj.fecha,
            observacion=obj.observacion,
            importe=obj.importe,
            # Nunca se confia en un signo del cliente - siempre el del concepto real.
            signo=concepto.signo,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(db_mov)
        db.flush()

        db.execute(
            text("CALL public.sp_comercial_movcaja(:operacion, :parm_id)"),
            {"operacion": "N", "parm_id": db_mov.id}
        )

        db.commit()
        db.refresh(db_mov)
        return db_mov

    except HTTPException:
        raise
    except (IntegrityError, DataError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise TransaccionValidationError(str(e.orig))
