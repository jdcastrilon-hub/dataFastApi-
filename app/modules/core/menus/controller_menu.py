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
def obtener_menu(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repositoty_menu.obtener_menu(db)