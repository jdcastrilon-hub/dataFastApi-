from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_sucursal, schema_sucursal
from app.modules.core.usuarios import model_usuario
from app.core.auth import security


router = APIRouter(
    prefix="/core/sucursal",
    tags=["Sucursales"])

@router.get("/pagination", response_model=schema_sucursal.PaginatedSucursalResponse)
def list_sucursales_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    id_emp: int = Query(...),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_sucursal.get_sucursales_paginated(db, page, size, id_emp, texto)

@router.get("/search", response_model=schema_sucursal.SucursalBase)
def obtener_sucursal(
    id_sucursal: int,
    id_emp: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una sucursal especifica x ID, solo si pertenece a la empresa actual."""
    db_sucursal = repository_sucursal.get_sucursal(db, id_sucursal=id_sucursal, id_emp=id_emp)
    if db_sucursal is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return db_sucursal

@router.post("/save")
def crear_sucursal(sucursal: schema_sucursal.SucursalCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea una nueva sucursal. No se atrapa la excepcion aqui a proposito: los errores
    de integridad (ej. codigo duplicado en la misma empresa) los resuelve el
    manejador global con un mensaje amigable."""
    repository_sucursal.create_sucursal(db=db, obj=sucursal)
    return {
        "status": "success",
        "message": "Sucursal creada exitosamente",
        "data": None
    }

@router.put("/edit/{id_sucursal}")
def actualizar_sucursal(id_sucursal: int, id_emp: int, sucursal: schema_sucursal.SucursalCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Edita una sucursal existente (ver nota en crear_sucursal sobre el manejo de errores)."""
    db_actual = repository_sucursal.update_sucursal(db, id_sucursal=id_sucursal, id_emp=id_emp, obj=sucursal)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return {
        "status": "success",
        "message": "Sucursal editada exitosamente",
        "data": None
    }

@router.delete("/delete/{id_sucursal}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sucursal(id_sucursal: int, id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina una sucursal del sistema."""
    success = repository_sucursal.delete_sucursal(db, id_sucursal=id_sucursal, id_emp=id_emp)
    if not success:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return None

@router.get("/list", response_model=List[schema_sucursal.SucursalBase])
def list_sucursales(page: int = 0, size: int = 100, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    print("page")
    return repository_sucursal.get_sucursales(db, page, size)

@router.get("/combo", response_model=List[schema_sucursal.SucursalListCombo])
def list_sucursales(page: int = 0, size: int = 100, db: Session = Depends(get_db),  contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    print("page")
    return repository_sucursal.get_sucursales(db, contexto.id_emp)

@router.get("/comboBybodegas", response_model=List[schema_sucursal.SucursalListComboByBodegas])
def list_sucursales_With_Bodegas(id_empresa: int ,db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_sucursal.get_sucursales_by_bodegas(db, id_empresa=id_empresa)

@router.get("/comboBycajas", response_model=List[schema_sucursal.SucursalListComboByCajas])
def list_sucursales_With_Bodegas(id_empresa: int, usuario: str = None, db: Session = Depends(get_db),usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_sucursal.get_sucursales_by_cajas(db, id_empresa=id_empresa, usuario=usuario)
