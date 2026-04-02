from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from . import repository_monitor, schema_monitor

router = APIRouter(
    prefix="/compras/monitor",
    tags=["compras - Monitor"])

@router.get("/comprasrealizadas", response_model=schema_monitor.MonitorComprasRealizadas)
def get_monitorcomprasrealizadas_data(
   # tipo_reporte: str,
    fechainicial: date,
    fechafinal: date,
    id_bodega: Optional[int] = 0,
    id_proveedor: Optional[int] = 0,
    articulo: Optional[int] = 0,
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):  
    print ("get_monitorcomprasrealizadas_data")
    print(fechainicial)
    return repository_monitor.get_monitorcomprasrealizadas_data(db, fechainicial, fechafinal,id_bodega,id_proveedor,articulo,page,size)