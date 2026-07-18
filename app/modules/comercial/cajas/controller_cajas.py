from fastapi import APIRouter, Depends, HTTPException, Query,status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from . import schema_cajas, repository_cajas
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/cajas",
    tags=["comercial - Cajas"])

#Cajas asociadas a un usuario (para venta-directa sin turno abierto)
@router.get("/porusuario", response_model=list[schema_cajas.CajaCombo])
def cajas_por_usuario(
    id_usuario: int,
    idempresa: int = 1,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_cajas.get_cajas_por_usuario(db, id_usuario=id_usuario, idempresa=idempresa)

#Buscar caja por ID
@router.get("/search", response_model=schema_cajas.CajaBase)
def obtener_caja(id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una caja específica x ID."""
    bd_caja = repository_cajas.get_caja_by_id(db, id=id)
    if bd_caja is None:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    return bd_caja

@router.get("/pagination", response_model=schema_cajas.PaginatedCajaResponse)
def list_cajas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa: int = 1,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_cajas.get_cajas_paginated(db, page, size, idempresa, texto)

@router.post("/save")
def crear_caja(caja: schema_cajas.CajaCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea una nueva Caja. No se atrapa la excepcion aqui a proposito: los errores
    de integridad los resuelve el manejador global con un mensaje amigable."""
    repository_cajas.create_caja(db=db, obj=caja)
    return {
            "status": "success",
            "message": "Caja creada exitosamente",
            "data": None  # Omites el objeto completo para ahorrar recursos
    }

@router.put("/edit/{id}")
def actualizar_caja(id: int, caja: schema_cajas.CajaCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Editar una caja."""
    repository_cajas.update_caja(db=db, id=id, obj=caja)
    return {
        "status": "success",
        "message": "Caja editada exitosamente",
        "data": None
    }

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_caja(id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina una caja del sistema."""
    success = repository_cajas.delete_caja(db, id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Caja no encontrada")
    return None
