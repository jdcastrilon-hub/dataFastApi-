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

@router.get("/pagination", response_model=schema_articulos.PaginatedArticuloResponse)
def list_bodegas_paginacion(  
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)):
    return repository_articulos.get_articulos_paginated(db, page, size)

@router.get("/search", response_model=schema_articulos.ArticulosBase)
def obtener_bodega(id_articulo: int, db: Session = Depends(get_db)):
    """Busca un articulo específico x ID."""
    bd_articulo = repository_articulos.get_articulo(db, id_articulo=id_articulo)
    if bd_articulo is None:
        raise HTTPException(status_code=404, detail="Articulo no encontrado")
    return bd_articulo

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

#Valida el stock actual de los codigos de barra y valida si han tenido movimientos en el stock
@router.get("/stock-masivo", response_model=List[schema_articulos.ArticuloActualizacionDatos])
def get_stock_masivo(id_articulo: int,cadena: str,db: Session = Depends(get_db)):
    return repository_articulos.consultar_stock_codigosbarra(db, cadena, id_articulo)  

@router.post("/save")
def save_articulo(articulo: schema_articulos.ArticuloCreate, db: Session = Depends(get_db)):
    """Crea una nueva bodega y retorna el objeto con su ID generado."""
    repository_articulos.create_articulo(db=db, obj=articulo)
    return {
            "status": "success",
            "message": "Articulo creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }

    
@router.put("/edit/{id_articulo}")
def actualizar_articulo(id_articulo: int, articulo: schema_articulos.ArticuloCreate, db: Session = Depends(get_db)):
    """Actualiza los datos de una bodega existente."""
    repository_articulos.update_articulo(db, id_articulo=id_articulo, obj=articulo)
    return {
                "status": "success",
                "message": "Articulo actualizado exitosamente",
                "data": None  # Omites el objeto completo para ahorrar recursos
    } 

@router.delete("/delete/{id_articulo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bodega(id_articulo: int, db: Session = Depends(get_db)):
    """Elimina un artiulo del sistema."""
    success = repository_articulos.delete_articulo(db, id_articulo=id_articulo)
    if not success:
        raise HTTPException(status_code=404, detail="Articulo no encontrada")
    return None  