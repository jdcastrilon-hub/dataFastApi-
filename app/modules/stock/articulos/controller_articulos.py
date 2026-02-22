from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_articulos ,schema_articulos

router = APIRouter(
    prefix="/bodega/articulos",
    tags=["Core - Empresas"])

@router.get("/list", response_model=List[schema_articulos.ArticulosBase])
def listar_empresas( db: Session = Depends(get_db)):
    """Obtiene la lista de todas los articulos."""
    return repository_articulos.get_articulos(db)

@router.get("/list2", response_model=List[schema_articulos.ArticuloBaseCompleto])
def listar_empresas( db: Session = Depends(get_db)):
    """Obtiene la lista de todas los articulos."""
    return repository_articulos.get_articulosCompleto(db)

@router.post("/save")
def save_articulo(articulo: schema_articulos.ArticuloCreate, db: Session = Depends(get_db)):
    """Crea una nueva bodega y retorna el objeto con su ID generado."""
    try:
        repository_articulos.create_articulo(db=db, articulo=articulo)
        return {
            "status": "success",
            "message": "Articulo creada exitosamente",
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