from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from . import schema_categoria, repository_categoria

router = APIRouter(
    prefix="/bodega/categorias",
    tags=["Stock - Categorias"])

@router.get("/pagination", response_model=schema_categoria.PaginatedBodegaResponse)
def list_bodegas_paginacion(  
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)):
    return repository_categoria.get_bodegas_paginated(db, page, size)

@router.get("/search", response_model=schema_categoria.CategoriaBase)
def obtener_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """Busca una categoria específica x ID."""
    db_categoria= repository_categoria.get_categoriaByID(db, categoria_id)
    if db_categoria is None:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return db_categoria

@router.post("/save")
def crear_categoria(categoria: schema_categoria.CategoriaCreate, db: Session = Depends(get_db)):
    """Crea una nueva categoria"""
    try:
        repository_categoria.create_categoria(db=db, cat=categoria)
        return {
            "status": "success",
            "message": "Categoria creada exitosamente",
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
   