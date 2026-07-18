from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy import Date, String, cast, desc, exists, or_, text, true
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session , joinedload
from . import model_turno, squema_turno
from app.core.numeradores import repository_numerador
from app.modules.comercial.cajas import model_cajas
from app.modules.comercial.clientes import model_cliente
from app.modules.comercial.mediopago import model_medio


def _siguiente_nro_turno(db: Session, id_caja: int) -> int:
    """El numero de turno usa el numerador por empresa (md_numeradores, codigo
    'TURNO') igual que compradirecta/ajustestock/trasladobodega. La empresa se
    resuelve via la caja, ya que TAbrirTurno no la trae directo en su tabla."""
    id_emp = db.query(model_cajas.MCaja.id_emp).filter(model_cajas.MCaja.id == id_caja).scalar()
    if id_emp is None:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, "TURNO")
    return siguiente


#Paginacion
def get_turnos_paginated(db: Session, page: int, size: int, idempresa: int, usuario: str, texto: str = None):
    # Lista solo los turnos ABIERTOS del usuario logueado (no el historico completo).
    # TODO: cuando se implementen roles, si el usuario_autenticado es administrador
    # este filtro por "usuario" debe omitirse para que vea el listado completo.
    query = db.query(model_turno.TAbrirTurno)\
        .join(model_turno.TAbrirTurno.caja)\
        .filter(
            model_cajas.MCaja.id_emp == idempresa,
            model_turno.TAbrirTurno.usuario == usuario,
            model_turno.TAbrirTurno.status == True
        )

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                cast(model_turno.TAbrirTurno.id, String).ilike(patron),
                model_turno.TAbrirTurno.usuario.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query\
        .options(joinedload(model_turno.TAbrirTurno.caja))\
        .order_by(desc(model_turno.TAbrirTurno.fecha_mod))\
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

# Obtener un turno por ID
def get_turno_by_id(db: Session, id: int):
    return db.query(model_turno.TAbrirTurno).filter(model_turno.TAbrirTurno.id == id).options(
        joinedload(model_turno.TAbrirTurno.caja)
    ).first()

# Actualizar turno. No incluye "cerrar turno" (cambio de status abierto/cerrado):
# eso queda fuera de alcance por ahora (ver project_data_comercial_module), esto
# solo permite corregir los datos de un turno ya abierto.
def update_turno(db: Session, id: int, obj: squema_turno.TurnoCreate):
    try:
        db_turno = db.query(model_turno.TAbrirTurno).filter(model_turno.TAbrirTurno.id == id).first()
        if not db_turno:
            raise HTTPException(status_code=404, detail="Turno no encontrado")

        db_turno.id_caja = obj.id_caja
        db_turno.fec_doc = obj.fec_doc
        db_turno.imp_base = obj.imp_base
        db_turno.observacion = obj.observacion
        db_turno.usuario = obj.usuario
        db_turno.logs = [log.model_dump() for log in obj.logs]
        db_turno.fecha_mod = obj.fecha_mod

        db.commit()
        db.refresh(db_turno)
        return db_turno

    except HTTPException:
        raise
    except (IntegrityError, DataError):
        db.rollback()
        raise

def create_turno(db: Session, obj: squema_turno.TurnoCreate):

    turno_abierto = db.query(model_turno.TAbrirTurno).filter(
        model_turno.TAbrirTurno.usuario == obj.usuario,
        model_turno.TAbrirTurno.status == True
    ).first()
    if turno_abierto:
        raise HTTPException(
            status_code=400,
            detail=f"Ya tienes un turno abierto (Nro. {turno_abierto.id}). Debes cerrarlo antes de abrir uno nuevo."
        )

    nro_docum = _siguiente_nro_turno(db, obj.id_caja)
    # Convertimos la lista de objetos LogEntry a una lista de diccionarios
    logs_dict = [log.model_dump() for log in obj.logs]
    # 1. Crear el objeto principal
    db_turno = model_turno.TAbrirTurno(
        id=nro_docum,
        id_caja=obj.id_caja,
        fec_doc=obj.fec_doc,
        # Se fija aca, server-side, en el momento real de creacion - no se toma del
        # payload del cliente (evita depender del reloj del navegador) y nunca se
        # vuelve a tocar despues (ver update_turno).
        fecha_apertura=datetime.utcnow(),
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

        # Turno vencido: sigue abierto (status=true) pero supero las horas
        # permitidas para la caja (m_cajas.horas_turno, sin limite si es null o si
        # fecha_apertura nunca se registro - ej. turnos historicos previos a este
        # campo). El llamador (venta-directa/venta-pos) decide que hacer con esto;
        # el formulario de cierre ignora este flag a proposito.
        horas_transcurridas = None
        turno_vencido = False
        if turno.fecha_apertura:
            horas_transcurridas = (datetime.utcnow() - turno.fecha_apertura).total_seconds() / 3600
            if turno.caja.horas_turno is not None and horas_transcurridas > turno.caja.horas_turno:
                turno_vencido = True

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
            "mediopago":mediopago,
            "turnoVencido": turno_vencido,
            "horasTranscurridas": round(horas_transcurridas, 1) if horas_transcurridas is not None else None,
            "horasLimite": turno.caja.horas_turno
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