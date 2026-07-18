from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_devolucion, schema_devolucion
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/compras/devolucioncompras",
    tags=["Compras - Devolucion a Proveedor"])

@router.get("/comprasorigen", response_model=List[schema_devolucion.CompraOrigenBusqueda])
def buscar_compras_origen(
    id_proveedor: int,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Compras Finalizadas del proveedor, candidatas a ser la compra origen de una
    devolucion. texto filtra por numero de documento o remito."""
    return repository_devolucion.get_compras_origen_by_proveedor(db, id_proveedor=id_proveedor, texto=texto)

@router.get("/lineasdisponibles", response_model=List[schema_devolucion.LineaDisponibleDevolucion])
def obtener_lineas_disponibles(
    id_compra_origen: int,
    excluir_id_trans: int = None,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Lineas de la compra origen, con el stock disponible actual de cada una y lo
    ya devuelto en otras devoluciones de esta misma compra descontado. excluir_id_trans
    se envia al editar una devolucion existente, para no restarse a si misma."""
    return repository_devolucion.get_lineas_disponibles(db, id_compra_origen=id_compra_origen, excluir_id_trans=excluir_id_trans)

@router.get("/pagination", response_model=schema_devolucion.PaginatedDevolucionCompraResponse)
def list_devoluciones_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    id_emp: int = 0,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_devolucion.get_devoluciones_paginated(db, page, size, id_emp, texto)

@router.get("/search", response_model=schema_devolucion.DevolucionCompraBase)
def obtener_devolucion(transaccion: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca una devolucion especifica x ID."""
    bd_devolucion = repository_devolucion.get_devolucion_by_id(db, id_trans=transaccion)
    if bd_devolucion is None:
        raise HTTPException(status_code=404, detail="Devolucion no encontrada")
    return bd_devolucion

@router.post("/save")
def crear_devolucion(devolucion: schema_devolucion.DevolucionCompraCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea una nueva devolucion a proveedor: impacta p_stock/p_costos de inmediato
    (no hay Borrador/Finalizado). No se atrapa la excepción aquí a propósito: así
    los errores del SP o de integridad los resuelve el manejador global correspondiente
    (TransaccionValidationError/IntegrityError) con un mensaje amigable."""
    repository_devolucion.create_devolucion(db=db, obj=devolucion)
    return {
        "status": "success",
        "message": "Devolución creada exitosamente",
        "data": None
    }

@router.put("/edit/{id_trans}")
def actualizar_devolucion(id_trans: int, devolucion: schema_devolucion.DevolucionCompraCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Edita una devolucion existente (ver nota en crear_devolucion sobre el manejo de errores)."""
    resultado = repository_devolucion.update_devolucion(db=db, id_trans=id_trans, obj=devolucion)
    if resultado is None:
        raise HTTPException(status_code=404, detail="Devolucion no encontrada")
    return {
        "status": "success",
        "message": "Devolución editada exitosamente",
        "data": None
    }

@router.delete("/delete/{id_trans}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_devolucion(id_trans: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina una devolucion (revierte su impacto en p_stock/p_costos)."""
    success = repository_devolucion.delete_devolucion(db, id_trans=id_trans)
    if not success:
        raise HTTPException(status_code=404, detail="Devolucion no encontrada")
    return None
