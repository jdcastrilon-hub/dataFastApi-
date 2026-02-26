from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_bodega, schema_bodega

router = APIRouter(
    prefix="/bodega/bodegas",
    tags=["Stock - Bodegas"])
#skip: int = 0: Es un parámetro de consulta (Query Param). Le dice a la base de datos cuántos registros saltarse. Útil para la paginación (ej. saltarse los primeros 20).
#limit: int = 100: Define el máximo de registros a devolver por "página". Por defecto, si el usuario no envía nada, traerá 100.
#Session = Depends(get_db) : Dependencia de base de datos
#""" = Documentacion del API

@router.get("/list", response_model=List[schema_bodega.BodegaResponse])
def listar_bodegas(page: int = 0, size: int = 100, db: Session = Depends(get_db)):
    """Obtiene la lista de todas las bodegas."""
    return repository_bodega.get_bodegas(db, skip=page, limit=size)

@router.get("/listCombo", response_model=List[schema_bodega.BodegaCombo])
def listar_bodegas(db: Session = Depends(get_db)):
    """Obtiene la lista de todas las bodegas."""
    return repository_bodega.get_bodegas_combo(db)


@router.get("/pagination", response_model=schema_bodega.PaginatedBodegaResponse)
def list_bodegas_paginacion(  
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)):
    return repository_bodega.get_bodegas_paginated(db, page, size)

@router.get("/search", response_model=schema_bodega.BodegaResponse)
def obtener_bodega(bodega_id: int, db: Session = Depends(get_db)):
    """Busca una bodega específica x ID."""
    db_bodega = repository_bodega.get_bodega(db, bodega_id=bodega_id)
    if db_bodega is None:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return db_bodega


@router.post("/save")
def crear_bodega(bodega: schema_bodega.BodegaCreate, db: Session = Depends(get_db)):
    """Crea una nueva bodega y retorna el objeto con su ID generado."""
    try:
        repository_bodega.create_bodega(db=db, bodega=bodega)
        return {
            "status": "success",
            "message": "Bodega creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
        }
    except Exception as e:
        # Aquí devuelves un error controlado, por ejemplo 400 (Bad Request)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": f"Error al guardar: {str(e)}",
                "data": None
            }
        )

@router.put("/edit")
def actualizar_bodega(bodega_id: int, bodega: schema_bodega.BodegaCreate, db: Session = Depends(get_db)):
    """Actualiza los datos de una bodega existente."""
    try:
        repository_bodega.update_bodega(db, bodega_id=bodega_id, bodega_data=bodega)
        return {
                "status": "success",
                "message": "Bodega editada exitosamente",
                "data": None  # Omites el objeto completo para ahorrar recursos
        }
    except Exception as e:
            # Aquí devuelves un error controlado, por ejemplo 400 (Bad Request)
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "error",
                    "message": f"Error al guardar: {str(e)}",
                    "data": None
                }
        )
    
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bodega(bodega_id: int, db: Session = Depends(get_db)):
    """Elimina una bodega del sistema."""
    success = repository_bodega.delete_bodega(db, bodega_id=bodega_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return None

@router.get("/stockDisponiblexBodega", response_model=List[schema_bodega.StockDisponibleResponse])
def get_stock_disponible(
    idArticulo: int ,
    idBodega: int ,
    idEstado: int ,
    db: Session = Depends(get_db)
):
    return repository_bodega.get_stock_disponible(db,idArticulo, idBodega, idEstado)