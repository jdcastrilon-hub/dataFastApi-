from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
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

@router.get("/menuxuser", response_model=list[schema_menu.MenuResponse])
def obtener_menu(id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Arbol de menu filtrado a lo que el usuario puede VER segun sus roles en la
    empresa activa (deny-by-default via md_rol_permiso)."""
    return repositoty_menu.obtener_menu(db, id_usuario=usuario_autenticado.id_usuario, id_emp=id_emp)