from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_bodega, schema_bodega
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos). m_bodegas no tiene
# columna id_emp propia (catalogo global) - el id_emp de estos endpoints es
# solo para el chequeo de permiso, no se persiste en la tabla.
MENU_CODIGO = "INV_BOD"

router = APIRouter(
    prefix="/bodega/bodegas",
    tags=["Stock - Bodegas"])
#skip: int = 0: Es un parámetro de consulta (Query Param). Le dice a la base de datos cuántos registros saltarse. Útil para la paginación (ej. saltarse los primeros 20).
#limit: int = 100: Define el máximo de registros a devolver por "página". Por defecto, si el usuario no envía nada, traerá 100.
#Session = Depends(get_db) : Dependencia de base de datos
#""" = Documentacion del API

@router.get("/list", response_model=List[schema_bodega.BodegaResponse])
def listar_bodegas(page: int = 0, size: int = 100, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas las bodegas."""
    return repository_bodega.get_bodegas(db, skip=page, limit=size)

@router.get("/listCombo", response_model=List[schema_bodega.BodegaCombo])
def listar_bodegas(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todas las bodegas."""
    return repository_bodega.get_bodegas_combo(db)


@router.get("/pagination", response_model=schema_bodega.PaginatedBodegaResponse)
def list_bodegas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_bodega.get_bodegas_paginated(db, page, size, texto)

@router.get("/search", response_model=schema_bodega.BodegaResponse)
def obtener_bodega(bodega_id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una bodega específica x ID."""
    db_bodega = repository_bodega.get_bodega(db, bodega_id=bodega_id)
    if db_bodega is None:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return db_bodega


@router.post("/save")
def crear_bodega(bodega: schema_bodega.BodegaCreate, id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea una nueva bodega y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    (ej. codBodega duplicado) los resuelve el manejador global de IntegrityError
    con un mensaje amigable, en una sola llamada (sin endpoint de validación previa)."""
    verificar_permiso(db, usuario_autenticado.id_usuario, id_emp, MENU_CODIGO, "CREAR")
    repository_bodega.create_bodega(db=db, bodega=bodega)
    return {
        "status": "success",
        "message": "Bodega creada exitosamente",
        "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit")
def actualizar_bodega(bodega_id: int, id_emp: int, bodega: schema_bodega.BodegaCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Actualiza los datos de una bodega existente (ver nota en crear_bodega sobre el manejo de errores)."""
    db_bodega = repository_bodega.get_bodega(db, bodega_id=bodega_id)
    if db_bodega is None:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    verificar_permiso(db, usuario_autenticado.id_usuario, id_emp, MENU_CODIGO, "EDITAR")

    repository_bodega.update_bodega(db, bodega_id=bodega_id, bodega_data=bodega)
    return {
            "status": "success",
            "message": "Bodega editada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_bodega(bodega_id: int, id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina una bodega del sistema."""
    verificar_permiso(db, usuario_autenticado.id_usuario, id_emp, MENU_CODIGO, "ELIMINAR")
    success = repository_bodega.delete_bodega(db, bodega_id=bodega_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bodega no encontrada")
    return None

@router.get("/stockDisponiblexBodega", response_model=List[schema_bodega.StockDisponibleResponse])
def get_stock_disponible(
    idArticulo: int ,
    idCodbarra: int ,
    idBodega: int ,
    idEstado: int ,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)
):
    return repository_bodega.get_stock_disponible(db,idArticulo,idCodbarra, idBodega, idEstado)