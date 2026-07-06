from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_sucursal, schema_sucursal
from app.modules.core.usuarios import model_usuario
from app.core.auth import security


router = APIRouter(
    prefix="/core/sucursal", 
    tags=["Sucursales"])

@router.get("/list", response_model=List[schema_sucursal.SucursalBase])
def list_sucursales(page: int = 0, size: int = 100, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    print("page")
    return repository_sucursal.get_sucursales(db, page, size)

@router.get("/combo", response_model=List[schema_sucursal.SucursalListCombo])
def list_sucursales(page: int = 0, size: int = 100, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    print("page")
    return repository_sucursal.get_sucursales(db, page, size)

@router.get("/comboBybodegas", response_model=List[schema_sucursal.SucursalListComboByBodegas])
def list_sucursales_With_Bodegas(id_empresa: int ,db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_sucursal.get_sucursales_by_bodegas(db, id_empresa=id_empresa)

@router.get("/comboBycajas", response_model=List[schema_sucursal.SucursalListComboByCajas])
def list_sucursales_With_Bodegas(id_empresa: int ,db: Session = Depends(get_db),usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_sucursal.get_sucursales_by_cajas(db, id_empresa=id_empresa)
