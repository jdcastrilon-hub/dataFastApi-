from datetime import date

from fastapi import HTTPException
from sqlalchemy import Date, desc, exists, text, true
from sqlalchemy.orm import Session , joinedload
from . import model_turno, squema_turno
from app.modules.comercial.clientes import model_cliente
from app.modules.comercial.mediopago import model_medio

def create_turno(db: Session, obj: squema_turno.TurnoCreate, nro_docum : int):

    # Convertimos la lista de objetos LogEntry a una lista de diccionarios
    logs_dict = [log.model_dump() for log in obj.logs]
    # 1. Crear el objeto principal
    db_turno = model_turno.TAbrirTurno(
        id=nro_docum,
        id_caja=obj.id_caja,
        fec_doc=obj.fec_doc,
        imp_base=obj.imp_base,
        observacion=obj.observacion,
        status=obj.status,
        usuario=obj.usuario,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_turno)
   
    db.commit()
    db.refresh(db_turno)
    return db_turno

def validar_turnoxusuario(db: Session, usuario: str):
    # 1. Buscamos directamente el registro del turno para el usuario y fecha
    turno = db.query(model_turno.TAbrirTurno).filter(
            model_turno.TAbrirTurno.status == True,
            model_turno.TAbrirTurno.usuario == usuario).options(
                joinedload(model_turno.TAbrirTurno.caja)).first()
    
    mediopago = db.query(model_medio.MedioPago).order_by(model_medio.MedioPago.orden).all()

    # 2. Si el turno existe, preparamos la respuesta con sus datos
    if turno:
        cliente= db.query(model_cliente.Cliente).filter(model_cliente.Cliente.id_cliente == turno.caja.id_cliente).first();
        print(cliente)
        return {
            "tieneturno": True,
            "idTurno": turno.id,      # Cambia 'id' por el nombre exacto de tu columna (ej: id_caja) si aplica
            "fec_doc": turno.fec_doc,
              # Datos que vienen desde la relación 'caja'
            "idSucursal" : turno.caja.id_sucursal_emp,
            "idBodega": turno.caja.id_bodega,
            "idEstado": turno.caja.id_estado,
            "documento": turno.caja.documento,
            "nomCaja":turno.caja.nom_caja,
            "cliente" : {
                 "idCliente": cliente.id_cliente,
                 "idPersona": cliente.id_persona,
                 "codTit": cliente.cod_tit,
                 "nombreCompleto": cliente.nom_cliente
                },
            "mediopago":mediopago
        }
    else:
        # 3. Si no existe, retornamos valores por defecto seguros
        return {
            "tieneturno": False,
            "idTurno": 0,
            "fec_doc": "1990-01-01",
            # Datos que vienen desde la relación 'caja'
            "idSucursal" : 0,
            "idBodega": 0,
            "idEstado": 0,
            "documento": "",
            "nomCaja":"",
            "cliente" : {
                    "idCliente": 0,
                    "idPersona": 0,
                    "codTit": "",
                    "nombreCompleto": ""
                    },
            "mediopago":mediopago
        }

def validar_ultimaCaja(db: Session, usuario: str):
    # Definimos el query nativo llamando a la función
    query = text("""
            SELECT 
                s.idturno as idturno,
                s.fecha,
                s.estado 
            FROM comercial_turnos_UltimaCaja(:param_usuario) AS s
    """)
        
    # Ejecutamos con los parámetros
    result = db.execute(query, {
            "param_usuario": usuario
    })
        
    # Convertimos los resultados a diccionarios para que Pydantic los valide
    return result.mappings().first()