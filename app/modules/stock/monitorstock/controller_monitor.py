from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from . import repository_monitor, schema_monitor

router = APIRouter(
    prefix="/bodega/monitor",
    tags=["Bodega - Monitor"])

@router.get("/filtrovista1", response_model=schema_monitor.filtrosgeneralesxempresa)
def filtrosvista1(id_empresa: int,db: Session = Depends(get_db)):

    data = repository_monitor.get_filtros_vista_inventario(db,id_empresa)
    
    if not data:
        # Devolver lista vacia , si no hay data
        return []
        
    return data


@router.get("/inventario", response_model=schema_monitor.MonitorInventario)
def get_monitorcomprasrealizadas_data(
   # tipo_reporte: str,
    bodega: int,
    negocio : int,
    categoria: int,
    subcategoria : int,
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):  
    print ("get_monitorcomprasrealizadas_data")
    return repository_monitor.get_monitorinventario_data(db, bodega, negocio,categoria,subcategoria,page,size)
