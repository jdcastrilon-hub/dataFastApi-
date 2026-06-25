from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import respository_medio, schema_medio

router = APIRouter(
    prefix="/comercial/mediopago",
    tags=["Comercial - MedioPago"])

@router.get("/list", response_model=List[schema_medio.MedioPagoCombo])
def search_medios_pago(db: Session = Depends(get_db)):
    return respository_medio.get_medios_pago(db)
