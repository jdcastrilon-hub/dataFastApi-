from fastapi import APIRouter, Depends, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repositoty_menu, schema_menu
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/menu",
    tags=["Core - Menu"])

# md_menu es una estructura de plataforma (compartida por TODAS las empresas, sin
# id_emp) - agregar filas ahi no es una operacion de administracion de empresa,
# ni siquiera el rol superadmin (que es por-empresa) deberia poder hacerlo. Este
# endpoint es exclusivamente para uso manual via Postman (no se integra al
# frontend), asi que en vez de requerir login/JWT se protege con la clave interna
# compartida (ver security.verificar_clave_admin_interna - la misma que usa
# POST /core/empresas/save).

@router.get("/menuxuser", response_model=list[schema_menu.MenuResponse])
def obtener_menu(id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Arbol de menu filtrado a lo que el usuario puede VER segun sus roles en la
    empresa activa (deny-by-default via md_rol_permiso)."""
    return repositoty_menu.obtener_menu(db, id_usuario=usuario_autenticado.id_usuario, id_emp=id_emp)

@router.post("/agregar")
def agregar_formulario(
    obj: schema_menu.AgregarFormularioRequest,
    db: Session = Depends(get_db),
    _: None = Depends(security.verificar_clave_admin_interna)):
    """Registra un formulario nuevo en md_menu + sus acciones en md_menu_permisos.
    Reemplaza el uso manual de scripts/agregar_formulario_menu.py. Uso exclusivo
    via Postman (header X-Admin-Key) - no requiere sesion de usuario ni se llama
    desde el frontend."""
    resultado = repositoty_menu.agregar_formulario_menu(db, obj)
    return {
        "status": "success",
        "message": "Formulario registrado exitosamente",
        "data": resultado
    }
