from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_costeo ,schema_costeo
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/bodega/tipocosteo",
    tags=["Bodega - Costeo"])

@router.get("/list", response_model=List[schema_costeo.CosteoBase])
def listar_Costeo(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas los coceptos."""
    return repository_costeo.get_costeo(db)