from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_usuario, esquema_usuario
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/usuarios",
    tags=["Core - usuario"])


@router.post("/save")
def create_cliente(db_cliente: esquema_usuario.UsuarioCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo cliente y retorna el objeto con su ID generado."""
    repository_usuario.create_usuario(db=db, obj=db_cliente)
    return {
            "status": "success",
            "message": "Cliente creado exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }