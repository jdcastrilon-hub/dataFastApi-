from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_servicios ,schema_servicios
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/bodega/tiposervicio",
    tags=["Bodega - TipoServicio"])

@router.get("/list", response_model=List[schema_servicios.ServicioBase])
def listar_Costeo(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas los coceptos."""
    return repository_servicios.get_sericios(db)