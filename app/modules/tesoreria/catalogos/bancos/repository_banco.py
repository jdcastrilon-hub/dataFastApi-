from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from . import model_banco, schema_banco
from app.core.numeradores import repository_numerador

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

# Codigo del numerador (por empresa) que identifica el consecutivo de cod_banco
CODIGO_NUMERADOR_BANCO = "BANCO"

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

def _obtener_cod_banco(db: Session, id_emp: int, cod_banco_manual):
    """
    Asigna el codBanco desde el numerador de la empresa (2 digitos, ver
    docs/tecnica/specs/core/autonumeracion-catalogos.md). Si la empresa tiene
    "requiere_consecutivo" en False, respeta lo que haya enviado el formulario
    (modo manual) - mismo criterio que _obtener_cod_estado/_obtener_cod_categoria.
    """
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_BANCO)
    if siguiente is None:
        return cod_banco_manual

    return repository_numerador.formatear_numerador(siguiente, longitud=2)

# Todos los bancos activos de la empresa (usado por el combo, ej. Medio de Pago)
def get_bancos(db: Session, id_emp: int):
    return db.query(model_banco.Banco)\
        .filter(model_banco.Banco.id_emp == id_emp, model_banco.Banco.activo == True)\
        .order_by(model_banco.Banco.nom_banco)\
        .all()

# Obtener un banco por ID
def get_banco(db: Session, banco_id: int):
    return db.query(model_banco.Banco).filter(model_banco.Banco.id == banco_id).options(
        joinedload(model_banco.Banco.usuarios).joinedload(model_banco.BancoXUser.usuario)
    ).first()

# Crear un banco
def create_banco(db: Session, obj: schema_banco.BancoCreate):
    logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])

    db_banco = model_banco.Banco(
        id_emp=obj.id_emp,
        cod_banco=_obtener_cod_banco(db, obj.id_emp, obj.cod_banco),
        nom_banco=obj.nom_banco,
        nro_cuenta=obj.nro_cuenta,
        activo=obj.activo,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_banco)
    db.flush()  # Para obtener el ID del banco antes de insertar los usuarios

    for usuario in obj.usuarios:
        db.add(model_banco.BancoXUser(id_banco=db_banco.id, id_usuario=usuario.id_usuario))

    db.commit()
    db.refresh(db_banco)  # Aquí se recupera el ID generado por el autonumérico
    return db_banco

# Actualizar banco
def update_banco(db: Session, banco_id: int, obj: schema_banco.BancoCreate):
    db_banco = db.query(model_banco.Banco).filter(model_banco.Banco.id == banco_id).first()

    if db_banco:
        db_banco.cod_banco = obj.cod_banco
        db_banco.nom_banco = obj.nom_banco
        db_banco.nro_cuenta = obj.nro_cuenta
        db_banco.activo = obj.activo
        db_banco.logs = _limitar_logs([log.model_dump() for log in obj.logs])
        db_banco.fecha_mod = obj.fecha_mod

        # Reemplazar usuarios asignados (borrar e reinsertar, mismo patron que cajas/conceptos)
        db.query(model_banco.BancoXUser).filter(model_banco.BancoXUser.id_banco == banco_id).delete()
        db.flush()
        for usuario in obj.usuarios:
            db.add(model_banco.BancoXUser(id_banco=banco_id, id_usuario=usuario.id_usuario))

        db.commit()
        db.refresh(db_banco)
    return db_banco

# Eliminar banco
def delete_banco(db: Session, banco_id: int):
    db_banco = db.query(model_banco.Banco).filter(model_banco.Banco.id == banco_id).first()
    if db_banco:
        db.delete(db_banco)  # cascade borra m_bancoxuser
        db.commit()
    return db_banco

#Paginacion
def get_bancos_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_banco.Banco).filter(model_banco.Banco.id_emp == id_emp)

    # Filtro de busqueda por codigo o nombre (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_banco.Banco.cod_banco.ilike(patron),
                model_banco.Banco.nom_banco.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query.order_by(desc(model_banco.Banco.fecha_mod)).offset(offset).limit(size).all()

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
