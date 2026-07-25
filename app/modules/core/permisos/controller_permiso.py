from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from . import repository_permiso, schema_permiso
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/permisos",
    tags=["Core - Permisos"])

@router.get("/mis-permisos", response_model=Dict[str, List[str]])
def mis_permisos(
    id_emp: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Todos los permisos (todas las acciones) del usuario autenticado en la empresa
    activa, agrupados por codigo de formulario. Pensado para traerse una sola vez
    por sesion/empresa y cachearse en el frontend (lo usa el guard de rutas)."""
    return repository_permiso.get_mis_permisos(db, id_usuario=usuario_autenticado.id_usuario, id_emp=id_emp)

@router.get("/modulos", response_model=List[schema_permiso.ModuloCombo])
def modulos_combo(
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Combo de modulos para el filtro de la matriz de permisos. md_modulo no tiene
    CRUD propio, solo se administra directo en la base de datos."""
    return repository_permiso.get_modulos_combo(db)

@router.get("/roles", response_model=List[schema_permiso.RolCombo])
def roles_combo(
    id_emp: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Combo de roles activos de la empresa para el filtro de la matriz de permisos."""
    return repository_permiso.get_roles_combo(db, id_emp)

@router.get("/matriz", response_model=List[schema_permiso.FormularioMatriz])
def obtener_matriz(
    id_rol: int,
    id_emp: int,
    id_modulo: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Matriz de permisos (formularios x acciones) de un rol, para el modulo seleccionado."""
    if not repository_permiso.rol_pertenece_a_empresa(db, id_rol, id_emp):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return repository_permiso.get_matriz(db, id_rol, id_modulo)

@router.put("/matriz")
def guardar_matriz(
    obj: schema_permiso.GuardarMatrizRequest,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Graba la matriz de permisos de un rol para el modulo seleccionado (borra e
    reinserta solo los permisos de ese modulo, no toca los de otros modulos)."""
    if not repository_permiso.rol_pertenece_a_empresa(db, obj.id_rol, obj.id_emp):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    repository_permiso.guardar_matriz(db, obj.id_rol, obj.id_modulo, obj.otorgados)
    return {
        "status": "success",
        "message": "Permisos guardados exitosamente",
        "data": None
    }
