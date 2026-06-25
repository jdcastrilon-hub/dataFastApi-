from fastapi import HTTPException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session , joinedload
from . import model_cajas, schema_cajas


def create_caja(db: Session, obj: schema_cajas.CajaCreate):

    # Convertimos la lista de objetos LogEntry a una lista de diccionarios
    logs_dict = [log.model_dump() for log in obj.logs]
    # 1. Crear el objeto principal
    db_caja = model_cajas.MCaja(
        id_emp=obj.id_emp,
        id_sucursal_emp=obj.id_sucursal_emp,
        cod_caja=obj.cod_caja,
        nom_caja=obj.nom_caja,
        cajapos=obj.cajapos,
        id_cliente=obj.id_cliente,
        id_bodega=obj.id_bodega,
        id_estado=obj.id_estado,
        documento=obj.documento,
        status=obj.status,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_caja)
    db.flush() # Envio a base de datos

    # 2. Crear las subcategorías vinculadas
    for usuarios in obj.usuarios:
        db_usuarios = model_cajas.MCajasXUser(
            id_caja=db_caja.id,
            usuario=usuarios.usuario
        )
        db.add(db_usuarios)

    db.commit()
    db.refresh(db_caja)
    return db_caja
