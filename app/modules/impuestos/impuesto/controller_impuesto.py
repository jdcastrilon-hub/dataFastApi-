from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_impuesto , schema_impuesto

router = APIRouter(
    prefix="/impuesto/tasas",
    tags=["Core - Impuesto"])

@router.get("/list", response_model=List[schema_impuesto.ImpuestoBase])
def lista_tasas(db: Session = Depends(get_db)):
    """Obtiene la lista de todas los impuestos."""
    return repository_impuesto.get_impuestos(db)