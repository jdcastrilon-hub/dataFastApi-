from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_sucursal, schema_sucursal



router = APIRouter(
    prefix="/core/sucursal", 
    tags=["Sucursales"])

@router.get("/list", response_model=List[schema_sucursal.SucursalBase])
def list_sucursales(page: int = 0, size: int = 100, db: Session = Depends(get_db)):
    print("page")
    return repository_sucursal.get_sucursales(db, page, size)

@router.get("/combo", response_model=List[schema_sucursal.SucursalListCombo])
def list_sucursales(page: int = 0, size: int = 100, db: Session = Depends(get_db)):
    print("page")
    return repository_sucursal.get_sucursales(db, page, size)

@router.get("/comboBybodegas", response_model=List[schema_sucursal.SucursalListComboByBodegas])
def list_sucursales_With_Bodegas(id_empresa: int ,db: Session = Depends(get_db)):
    return repository_sucursal.get_sucursales_by_bodegas(db, id_empresa=id_empresa)
