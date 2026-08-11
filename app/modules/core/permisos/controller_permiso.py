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

# Gate de acceso a la propia pantalla de Permisos (Pieza 3, paso 7). Ya existia
# como item de md_menu (ADM_PER) desde que se armo Administracion, pero nunca
# se exigia via verificar_permiso - cualquier usuario autenticado de la
# empresa podia leer/escribir la matriz de cualquier rol.
MENU_CODIGO_PERMISOS = "ADM_PER"

# NOTA DE SEGURIDAD (corregido 2026-08-02): estos endpoints recibian id_emp
# como query param/body enviado por el cliente, sin validar que el usuario
# autenticado perteneciera a esa empresa - cualquier usuario logueado de
# CUALQUIER empresa podia leer y sobrescribir la matriz de permisos de
# cualquier otra empresa con solo cambiar el id_emp en el request. Se corrige
# derivando id_emp exclusivamente del JWT (ContextoUsuario), igual que ya hace
# controller_auth.py - el cliente ya no puede elegir sobre que empresa opera.
# Corregido 2026-08-04 (Pieza 3): ahora si exigen verificar_permiso(ADM_PER, ...)
# en /modulos, /roles y /matriz (GET/PUT). /mis-permisos queda deliberadamente
# afuera: no es una accion administrativa, es el propio usuario pidiendo SU
# conjunto de permisos (lo usa cualquier rol, incluido uno sin acceso a
# Administracion, para poblar el cache que alimenta el sidebar/route guard) -
# gatearlo detras de ADM_PER rompería la navegacion de toda la app para
# cualquiera que no sea admin.

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
    CRUD propio, solo se administra directo en la base de datos. Ver
    get_modulos_combo: el superadmin ve todos los modulos (incluidos los
    deshabilitados para la empresa), un rol delegado no-superadmin solo ve los
    activos."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO_PERMISOS, "VER")
    return repository_permiso.get_modulos_combo(db, contexto.id_emp, contexto.usuario.id_usuario)

@router.get("/roles", response_model=List[schema_permiso.RolCombo])
def roles_combo(
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Combo de roles activos de la empresa para el filtro de la matriz de permisos."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO_PERMISOS, "VER")
    return repository_permiso.get_roles_combo(db, contexto.id_emp)

@router.get("/matriz", response_model=List[schema_permiso.FormularioMatriz])
def obtener_matriz(
    id_rol: int,
    id_modulo: int,
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Matriz de permisos (formularios x acciones) de un rol, para el modulo
    seleccionado - ya filtrada por el techo de delegacion de quien consulta
    (Pieza 3): un formulario/accion que el propio usuario no tiene, no aparece."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO_PERMISOS, "VER")
    if not repository_permiso.rol_pertenece_a_empresa(db, id_rol, contexto.id_emp):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return repository_permiso.get_matriz(db, id_rol, id_modulo, contexto.usuario.id_usuario, contexto.id_emp)

@router.put("/matriz")
def guardar_matriz(
    obj: schema_permiso.GuardarMatrizRequest,
    db: Session = Depends(get_db),
    contexto: ContextoUsuario = Depends(obtener_contexto_actual)):
    """Graba la matriz de permisos de un rol para el modulo seleccionado (borra e
    reinserta solo los permisos de ese modulo, no toca los de otros modulos).
    Techo de delegacion (Pieza 3): quien graba nunca puede tocar (otorgar NI
    revocar) un id_menu_permiso que el mismo no tiene - ver guardar_matriz."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO_PERMISOS, "EDITAR")
    if not repository_permiso.rol_pertenece_a_empresa(db, obj.id_rol, contexto.id_emp):
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    repository_permiso.guardar_matriz(db, obj.id_rol, obj.id_modulo, obj.otorgados, contexto.usuario.id_usuario, contexto.id_emp)
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
