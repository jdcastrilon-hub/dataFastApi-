from sqlalchemy.orm import Session, joinedload
from . import model_confcomercial, schema_confcomercial

MAX_LOGS_AUDITORIA = 10


def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def get_confcomercial(db: Session, id_emp: int):
    return (
        db.query(model_confcomercial.ConfComercial)
        .options(joinedload(model_confcomercial.ConfComercial.bodega_devoluciones))
        .filter(model_confcomercial.ConfComercial.id_emp == id_emp)
        .first()
    )


def get_roles_descuento(db: Session, id_emp: int):
    return (
        db.query(model_confcomercial.ConfComercialDctoRol)
        .options(joinedload(model_confcomercial.ConfComercialDctoRol.rol))
        .filter(model_confcomercial.ConfComercialDctoRol.id_emp == id_emp)
        .order_by(model_confcomercial.ConfComercialDctoRol.id_rol)
        .all()
    )


# Upsert: m_confcomercial es un singleton por empresa (PK = id_emp), asi que
# no hay distincion create/edit real - la primera vez que la empresa guarda su
# configuracion se crea la fila, despues siempre se actualiza la misma.
def upsert_confcomercial(db: Session, id_emp: int, obj: schema_confcomercial.ConfComercialBase):
    existente = db.query(model_confcomercial.ConfComercial).filter(
        model_confcomercial.ConfComercial.id_emp == id_emp
    ).first()

    if existente is None:
        existente = model_confcomercial.ConfComercial(id_emp=id_emp)
        db.add(existente)

    existente.precio_cero_editable = obj.precio_cero_editable
    existente.reimpresion_factura_permitida = obj.reimpresion_factura_permitida
    existente.id_bodega_devoluciones = obj.id_bodega_devoluciones or None
    existente.logs = _limitar_logs([log.model_dump() for log in obj.logs])
    existente.fecha_mod = obj.fecha_mod

    # Borrar e reinsertar la grilla completa - single round-trip para todo
    # el formulario (config + grilla de roles en una sola llamada de guardado).
    db.query(model_confcomercial.ConfComercialDctoRol).filter(
        model_confcomercial.ConfComercialDctoRol.id_emp == id_emp
    ).delete()

    for item in obj.roles_descuento:
        db.add(model_confcomercial.ConfComercialDctoRol(
            id_emp=id_emp,
            id_rol=item.id_rol,
            max_descuento=item.max_descuento
        ))

    db.commit()
    db.refresh(existente)
    return existente
