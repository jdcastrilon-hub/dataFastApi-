from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from . import repository_permiso, schema_permiso
from app.core.auth.security import obtener_contexto_actual, ContextoUsuario
from app.core.auth.permisos import verificar_permiso

router = APIRouter(
    prefix="/core/permisos",
    tags=["Core - Permisos"])

# Habilitacion de modulos por empresa - autoservicio del superadmin de cada
# empresa, no accion de plataforma. Ver docs/tecnica/specs/core/delegacion-permisos-menu-exclusivo.md.
MENU_CODIGO_MODULOS = "ADM_MOD"

# NOTA DE SEGURIDAD (corregido 2026-08-02): estos 5 endpoints recibian id_emp
# como query param/body enviado por el cliente, sin validar que el usuario
# autenticado perteneciera a esa empresa - cualquier usuario logueado de
# CUALQUIER empresa podia leer y sobrescribir la matriz de permisos de
# cualquier otra empresa con solo cambiar el id_emp en el request. Se corrige
# derivando id_emp exclusivamente del JWT (ContextoUsuario), igual que ya hace
# controller_auth.py - el cliente ya no puede elegir sobre que empresa opera.
# Pendiente aparte (ver spec de delegacion de permisos): estos endpoints
# todavia no exigen ningun permiso propio para ser llamados dentro de la
# propia empresa - cualquier usuario autenticado de la empresa puede hoy
# gestionar la matriz de permisos, no solo quien deberia.

@router.get("/mis-permisos", response_model=Dict[str, List[str]])
def mis_permisos(
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Todos los permisos (todas las acciones) del usuario autenticado en la empresa
    activa, agrupados por codigo de formulario. Pensado para traerse una sola vez
    por sesion/empresa y cachearse en el frontend (lo usa el guard de rutas)."""
    return repository_permiso.get_mis_permisos(db, id_usuario=contexto.usuario.id_usuario, id_emp=contexto.id_emp)

@router.get("/modulos", response_model=List[schema_permiso.ModuloCombo])
def modulos_combo(
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Combo de modulos para el filtro de la matriz de permisos. md_modulo no tiene
    CRUD propio, solo se administra directo en la base de datos."""
    return repository_permiso.get_modulos_combo(db)

@router.get("/roles", response_model=List[schema_permiso.RolCombo])
def roles_combo(
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Combo de roles activos de la empresa para el filtro de la matriz de permisos."""
    return repository_permiso.get_roles_combo(db, contexto.id_emp)

@router.get("/matriz", response_model=List[schema_permiso.FormularioMatriz])
def obtener_matriz(
    id_rol: int,
    id_modulo: int,
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Matriz de permisos (formularios x acciones) de un rol, para el modulo seleccionado."""
    if not repository_permiso.rol_pertenece_a_empresa(db, id_rol, contexto.id_emp):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return repository_permiso.get_matriz(db, id_rol, id_modulo)

@router.put("/matriz")
def guardar_matriz(
    obj: schema_permiso.GuardarMatrizRequest,
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Graba la matriz de permisos de un rol para el modulo seleccionado (borra e
    reinserta solo los permisos de ese modulo, no toca los de otros modulos)."""
    if not repository_permiso.rol_pertenece_a_empresa(db, obj.id_rol, contexto.id_emp):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    repository_permiso.guardar_matriz(db, obj.id_rol, obj.id_modulo, obj.otorgados)
    return {
        "status": "success",
        "message": "Permisos guardados exitosamente",
        "data": None
    }

@router.get("/modulos-empresa", response_model=List[schema_permiso.ModuloEmpresaResponse])
def modulos_empresa(
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Modulos del sistema y si estan habilitados para la empresa activa
    (autoservicio del superadmin de la empresa, ver ADM_MOD)."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO_MODULOS, "VER")
    return repository_permiso.get_modulos_empresa(db, contexto.id_emp)

@router.put("/modulos-empresa")
def actualizar_modulo_empresa(
    obj: schema_permiso.ModuloEmpresaUpdate,
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Habilita/deshabilita un modulo para la empresa activa."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO_MODULOS, "EDITAR")
    repository_permiso.set_modulo_habilitado(db, contexto.id_emp, obj.id_modulo, obj.activo)
    return {
        "status": "success",
        "message": "Módulo actualizado exitosamente",
        "data": None
    }
