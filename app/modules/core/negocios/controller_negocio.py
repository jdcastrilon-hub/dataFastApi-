from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_negocios , schema_negocio
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/negocios",
    tags=["Core - Empresas"])

@router.get("/listByNegocios", response_model=schema_negocio.NegocioxCategoriasDTO)
def listar_negocios_y_categorias(id_empresa: int,db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):

    data = repository_negocios.get_negocios_con_categorias_por_empresa(db,id_empresa)
    
    if not data:
        # Devolver lista vacia , si no hay data
        return []
        
    return data

    