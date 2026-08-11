from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_rol, schema_rol
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/roles",
    tags=["Core - Roles"])

@router.get("/listCombo", response_model=list[schema_rol.RolListCombo])
def roles_listcombo(
    id_emp: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Combo liviano de roles de la empresa (sin superadmin) para el picker
    dentro del formulario de Usuario."""
    return repository_rol.get_roles_listcombo(db, id_emp)

@router.get("/pagination", response_model=schema_rol.PaginatedRolResponse)
def list_roles_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    id_emp: int = Query(...),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_rol.get_roles_paginated(db, page, size, id_emp, usuario_autenticado.id_usuario, texto)

@router.get("/search", response_model=schema_rol.RolBase)
def obtener_rol(
    id_rol: int,
    id_emp: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un rol especifico x ID, solo si pertenece a la empresa actual."""
    db_rol = repository_rol.get_rol(db, id_rol=id_rol, id_emp=id_emp, id_usuario=usuario_autenticado.id_usuario)
    if db_rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return db_rol

@router.post("/save")
def crear_rol(rol: schema_rol.RolCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo rol. No se atrapa la excepcion aqui a proposito: los errores
    de integridad (ej. codigo duplicado en la misma empresa) los resuelve el
    manejador global con un mensaje amigable."""
    repository_rol.create_rol(db=db, obj=rol)
    return {
        "status": "success",
        "message": "Rol creado exitosamente",
        "data": None
    }

@router.put("/edit/{id_rol}")
def actualizar_rol(id_rol: int, id_emp: int, rol: schema_rol.RolCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Edita un rol existente (ver nota en crear_rol sobre el manejo de errores)."""
    repository_rol.update_rol(db=db, id_rol=id_rol, id_emp=id_emp, id_usuario=usuario_autenticado.id_usuario, obj=rol)
    return {
        "status": "success",
        "message": "Rol editado exitosamente",
        "data": None
    }

@router.delete("/delete/{id_rol}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_rol(id_rol: int, id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina un rol del sistema."""
    success = repository_rol.delete_rol(db, id_rol=id_rol, id_emp=id_emp, id_usuario=usuario_autenticado.id_usuario)
    if not success:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return None
