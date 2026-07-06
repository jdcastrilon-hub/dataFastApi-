from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_ajustecosto ,schema_ajustecosto
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/compras/ajustecosto",
    tags=["compras - Ajuste Costo"])

@router.post("/save")
def save(ajuste: schema_ajustecosto.AjusteBase, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea una nueva bodega y retorna el objeto con su ID generado."""
    repository_ajustecosto.create_ajuste(db=db, obj=ajuste)
    return {
            "status": "success",
            "message": "Ajuste creado exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }
