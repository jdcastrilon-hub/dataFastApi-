from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_compras, schema_compras
from app.core.Services.ServiceInicializacion import repository_serviciosIni

router = APIRouter(
    prefix="/compras/compradirecta",
    tags=["Compras - Proveedor"])

#Buscar Compras por ID
@router.get("/search", response_model=schema_compras.CompraBase)
def obtener_compra(transaccion: int, db: Session = Depends(get_db)):
    """Busca una compra específica x ID."""
    bd_compra = repository_compras.get_compras_by_id(db, transaccion=transaccion)
    if bd_compra is None:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return bd_compra

@router.get("/pagination", response_model=schema_compras.PaginatedCompraResponse)
def list_bodegas_paginacion(  
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa : int =0,
    db: Session = Depends(get_db)):
    return repository_compras.get_compras_paginated(db, page, size,idempresa)

@router.post("/save")
def crear_compra(compra: schema_compras.CompraCreate, db: Session = Depends(get_db)):
    """Crea una nueva compra y retorna el objeto con su ID generado."""
    try:
        result=repository_serviciosIni.NumeradorNextReal(db,"id_nrodocum_compra")
        print(result)
        repository_compras.create_compra(db=db, obj=compra,nro_docum=result)
        return {
            "status": "success",
            "message": "ajuste creada exitosamente",
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

@router.put("/edit/{id_trans}")
def crear_compra(id_trans: int,compra: schema_compras.CompraCreate, db: Session = Depends(get_db)):
    """Editar una compra y retorna el objeto con su ID generado."""
    try:
        repository_compras.update_compra(db=db,id_trans=id_trans, obj=compra)
        return {
            "status": "success",
            "message": "Compra editada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
        }
    except Exception as e:
        # Aquí devuelves un error controlado, por ejemplo 400 (Bad Request)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "status": "error",
                "message": f"Error al editar: {str(e)}",
                "data": None
            }
        )    

@router.get("/stock-masivo", response_model=List[schema_compras.CompraActualizacionDatos])
def get_stock_masivo(cadena: str, id_bodega: int, id_estado: int, db: Session = Depends(get_db)):
    return repository_compras.consultar_stock_lote(db, cadena, id_bodega, id_estado)  