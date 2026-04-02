from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_servicios ,schema_servicios

router = APIRouter(
    prefix="/bodega/tiposervicio",
    tags=["Bodega - TipoServicio"])

@router.get("/list", response_model=List[schema_servicios.ServicioBase])
def listar_Costeo(db: Session = Depends(get_db)):
    """Obtiene la lista de todas los coceptos."""
    return repository_servicios.get_sericios(db)