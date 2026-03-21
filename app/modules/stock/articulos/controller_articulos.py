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

@router.get("/searchCodigoBarra", response_model=List[schema_articulos.ArticuloSearchCodigoBarra])
def search_articulos(
    query: str, 
    db: Session = Depends(get_db)):
    return repository_articulos.find_codigoBarra_by_query(db,query)

@router.get("/searchCodigoStock", response_model=List[schema_articulos.ArticuloSearchCodigoStock])
def search_articulos(
    query: str, 
    db: Session = Depends(get_db)):
    return repository_articulos.find_articulos_by_query(db,query)

#Validar si existe un codigo de barra para un articulo
@router.get("/searchArticuloByCodigoBarra", response_model=schema_articulos.GeneracionCodigoBarra)
def existe_barra(id_articulo: int, cod_barra: str, db: Session = Depends(get_db)):
    existe = repository_articulos.check_exists_cod_barra(db, id_articulo, cod_barra)
    return repository_articulos.generacion_codigobarra(db,id_articulo,cod_barra)

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