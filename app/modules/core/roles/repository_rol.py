from fastapi import HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from . import model_rol, schema_rol

MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs: list) -> list:
    return logs[-MAX_LOGS_AUDITORIA:]


# True si el usuario tiene, en esta empresa, un rol marcado como superadmin
# (acceso total, ver model_rol.py::Rol.es_superadmin). Se usa tambien desde
# core/menus y core/permisos para saltar el chequeo normal de md_rol_permiso.
def usuario_es_superadmin(db: Session, id_usuario: int, id_emp: int) -> bool:
    return db.query(model_rol.Rol)\
        .join(model_rol.RolXUsuario, model_rol.RolXUsuario.id_rol == model_rol.Rol.id_rol)\
        .filter(
            model_rol.RolXUsuario.id_usuario == id_usuario,
            model_rol.Rol.id_emp == id_emp,
            model_rol.Rol.es_superadmin == True,
            model_rol.Rol.activo == True
        ).first() is not None


# Paginacion: solo los roles de la empresa de la sesion actual (cada empresa define
# sus propios roles independientemente). Los roles superadmin quedan invisibles
# salvo que quien pregunta sea, el mismo, superadmin en esta empresa.
def get_roles_paginated(db: Session, page: int, size: int, id_emp: int, id_usuario: int, texto: str = None):
    query = db.query(model_rol.Rol).filter(model_rol.Rol.id_emp == id_emp)

    if not usuario_es_superadmin(db, id_usuario, id_emp):
        query = query.filter(model_rol.Rol.es_superadmin == False)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_rol.Rol.codigo.ilike(patron),
                model_rol.Rol.nombre.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query.order_by(desc(model_rol.Rol.fecha_mod)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


# Obtener un rol por ID, solo si pertenece a la empresa indicada y (si es
# superadmin) solo si quien pregunta tambien lo es - no solo se esconde de las
# listas, tampoco se puede acceder adivinando el id.
def get_rol(db: Session, id_rol: int, id_emp: int, id_usuario: int):
    db_rol = db.query(model_rol.Rol)\
        .options(joinedload(model_rol.Rol.usuarios).joinedload(model_rol.RolXUsuario.usuario))\
        .filter(model_rol.Rol.id_rol == id_rol, model_rol.Rol.id_emp == id_emp)\
        .first()

    if db_rol and db_rol.es_superadmin and not usuario_es_superadmin(db, id_usuario, id_emp):
        return None

    return db_rol


# Un usuario no puede tener 2 roles (no-superadmin) a la vez en la misma
# empresa - no rompe el calculo de permisos (es puramente aditivo, get_mis_permisos
# ya haria la union sin problema), pero un rol amplio asignado "de paso" anularia
# en silencio la restriccion de un rol acotado, sin que se vea reflejado en
# ningun lado. superadmin queda afuera de esta regla (se asigna aparte, es un
# camino distinto). id_rol_actual se excluye del chequeo (reasignar el mismo
# usuario al mismo rol que se esta editando no es un conflicto).
def _usuario_tiene_otro_rol(db: Session, id_usuario: int, id_emp: int, id_rol_actual: int | None) -> str | None:
    query = db.query(model_rol.Rol.nombre)\
        .join(model_rol.RolXUsuario, model_rol.RolXUsuario.id_rol == model_rol.Rol.id_rol)\
        .filter(
            model_rol.RolXUsuario.id_usuario == id_usuario,
            model_rol.Rol.id_emp == id_emp,
            model_rol.Rol.es_superadmin == False,
        )
    if id_rol_actual is not None:
        query = query.filter(model_rol.Rol.id_rol != id_rol_actual)
    fila = query.first()
    return fila.nombre if fila else None


def _validar_un_rol_por_usuario(db: Session, id_emp: int, id_rol_actual: int | None, usuarios: list):
    for usuario in usuarios:
        otro_rol = _usuario_tiene_otro_rol(db, usuario.id_usuario, id_emp, id_rol_actual)
        if otro_rol:
            raise HTTPException(
                status_code=400,
                detail=f"El usuario ya tiene asignado el rol '{otro_rol}' - un usuario solo puede tener un rol por empresa."
            )


def create_rol(db: Session, obj: schema_rol.RolCreate):
    logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])

    _validar_un_rol_por_usuario(db, obj.id_emp, None, obj.usuarios)

    db_rol = model_rol.Rol(
        id_emp=obj.id_emp,
        codigo=obj.codigo,
        nombre=obj.nombre,
        descripcion=obj.descripcion,
        activo=obj.activo,
        # es_superadmin nunca viene del cliente (no existe en RolCreate) - un rol
        # nuevo creado desde la pantalla de Roles siempre nace en False.
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_rol)
    db.flush()

    for usuario in obj.usuarios:
        db.add(model_rol.RolXUsuario(id_rol=db_rol.id_rol, id_usuario=usuario.id_usuario))

    db.commit()
    db.refresh(db_rol)
    return db_rol


def update_rol(db: Session, id_rol: int, id_emp: int, id_usuario: int, obj: schema_rol.RolCreate):
    db_rol = get_rol(db, id_rol=id_rol, id_emp=id_emp, id_usuario=id_usuario)
    if not db_rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")

    _validar_un_rol_por_usuario(db, id_emp, id_rol, obj.usuarios)

    db_rol.codigo = obj.codigo
    db_rol.nombre = obj.nombre
    db_rol.descripcion = obj.descripcion
    db_rol.activo = obj.activo
    db_rol.logs = _limitar_logs([log.model_dump() for log in obj.logs])
    db_rol.fecha_mod = obj.fecha_mod

    # Reemplaza los usuarios asignados (borrar e reinsertar, igual que conceptos/cajas)
    db.query(model_rol.RolXUsuario).filter(model_rol.RolXUsuario.id_rol == id_rol).delete()
    db.flush()
    for usuario in obj.usuarios:
        db.add(model_rol.RolXUsuario(id_rol=id_rol, id_usuario=usuario.id_usuario))

    db.commit()
    db.refresh(db_rol)
    return db_rol


def delete_rol(db: Session, id_rol: int, id_emp: int, id_usuario: int):
    db_rol = get_rol(db, id_rol=id_rol, id_emp=id_emp, id_usuario=id_usuario)
    if not db_rol:
        return None

    if db_rol.es_protegido:
        raise HTTPException(status_code=400, detail="Este rol es la base de la empresa y no se puede eliminar")

    db.delete(db_rol)  # cascade borra md_usuarioxrol
    db.commit()
    return db_rol


# Combo liviano para el picker de rol del formulario de Usuario - ver
# schema_rol.RolListCombo.
def get_roles_listcombo(db: Session, id_emp: int):
    return db.query(model_rol.Rol)\
        .filter(model_rol.Rol.id_emp == id_emp, model_rol.Rol.activo == True, model_rol.Rol.es_superadmin == False)\
        .order_by(model_rol.Rol.nombre)\
        .all()
