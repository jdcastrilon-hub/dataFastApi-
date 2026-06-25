from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from . import schema_cajas, repository_cajas

router = APIRouter(
    prefix="/comercial/cajas",
    tags=["comercial - Cajas"])

@router.post("/save")
def crear_caja(caja: schema_cajas.CajaCreate, db: Session = Depends(get_db)):
    """Crea una nueva Caja"""
    repository_cajas.create_caja(db=db, obj=caja)
    return {
            "status": "success",
            "message": "Caja creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }
  
   