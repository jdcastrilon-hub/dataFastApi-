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
    repository_categoria.create_categoria(db=db, cat=categoria)
    return {
            "status": "success",
            "message": "Categoria creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }
  
   
@router.put("/edit/{id_categoria}")
def actualizar_categoria(id_categoria: int, categoria: schema_categoria.CategoriaCreate, db: Session = Depends(get_db)):
    """Actualiza los datos de una categoria """
    repository_categoria.update_categoria(db, id_categoria=id_categoria, obj=categoria)
    return {
                "status": "success",
                "message": "Categoria actualizado exitosamente",
                "data": None  # Omites el objeto completo para ahorrar recursos
    } 

@router.delete("/delete/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(id_categoria: int, db: Session = Depends(get_db)):
    """Elimina una categoria del sistema."""
    success = repository_categoria.delete_categoria(db, id_categoria=id_categoria)
    if not success:
        raise HTTPException(status_code=404, detail="La categoria no existe")
    return None  