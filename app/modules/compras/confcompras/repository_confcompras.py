from sqlalchemy.orm import Session, joinedload
from . import model_confcompras, schema_confcompras

MAX_LOGS_AUDITORIA = 10


def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def get_confcompras(db: Session, id_emp: int):
    return (
        db.query(model_confcompras.ConfCompras)
        .options(joinedload(model_confcompras.ConfCompras.estado_comp))
        .filter(model_confcompras.ConfCompras.id_emp == id_emp)
        .first()
    )


# Upsert: m_confcompras es un singleton por empresa (PK = id_emp), asi que no
# hay distincion create/edit real - la primera vez que la empresa guarda su
# configuracion se crea la fila, despues siempre se actualiza la misma.
def upsert_confcompras(db: Session, id_emp: int, obj: schema_confcompras.ConfComprasBase):
    existente = db.query(model_confcompras.ConfCompras).filter(
        model_confcompras.ConfCompras.id_emp == id_emp
    ).first()

    if existente is None:
        existente = model_confcompras.ConfCompras(id_emp=id_emp)
        db.add(existente)

    existente.id_estado_comp = obj.id_estado_comp or None
    existente.act_precio_compra = obj.act_precio_compra
    existente.porc_utilidad_general = obj.porc_utilidad_general
    existente.logs = _limitar_logs([log.model_dump() for log in obj.logs])
    existente.fecha_mod = obj.fecha_mod

    db.commit()
    db.refresh(existente)
    return existente
