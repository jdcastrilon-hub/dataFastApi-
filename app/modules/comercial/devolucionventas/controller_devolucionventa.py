from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_devolucionventa as repository_devolucion, schema_devolucionventa as schema_devolucion
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "VEN_NOTACR"

router = APIRouter(
    prefix="/comercial/devolucionventas",
    tags=["Comercial - Nota Credito"])


@router.get("/facturasorigen", response_model=List[schema_devolucion.FacturaOrigenBusqueda])
def buscar_facturas_origen(
    id_cliente: int,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Facturas del cliente, candidatas a ser la factura origen de una nota
    credito. texto filtra por numero de documento o serie."""
    return repository_devolucion.get_facturas_origen_by_cliente(db, id_emp=contexto.id_emp, id_cliente=id_cliente, texto=texto)


@router.get("/lineasdisponibles", response_model=List[schema_devolucion.LineaDisponibleNotaCredito])
def obtener_lineas_disponibles(
    id_trans_ref: int,
    excluir_id_trans: int = None,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Lineas de la factura origen, con el saldo disponible para devolver de cada
    una (lo ya devuelto en otras notas de esta misma factura descontado).
    excluir_id_trans se envia al editar una nota existente, para no restarse a
    si misma."""
    return repository_devolucion.get_lineas_disponibles(db, id_emp=contexto.id_emp, id_trans_ref=id_trans_ref, excluir_id_trans=excluir_id_trans)


@router.get("/pagination", response_model=schema_devolucion.PaginatedNotaFacturaResponse)
def list_notas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_devolucion.get_notas_paginated(db, page, size, contexto.id_emp, texto)


@router.get("/search", response_model=schema_devolucion.NotaFacturaBase)
def obtener_nota(transaccion: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca una nota credito especifica x ID."""
    bd_nota = repository_devolucion.get_nota_by_id(db, id_trans=transaccion)
    if bd_nota is None or bd_nota.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Nota credito no encontrada")
    return bd_nota


@router.post("/save")
def crear_nota(nota: schema_devolucion.NotaFacturaCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea una nueva nota credito: impacta p_stock de inmediato (no hay Borrador/
    Finalizado). No se atrapa la excepcion aqui a proposito: asi los errores del
    SP o de integridad los resuelve el manejador global correspondiente."""
    nota.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_devolucion.create_nota(db=db, obj=nota)
    return {
        "status": "success",
        "message": "Nota crédito creada exitosamente",
        "data": None
    }


@router.put("/edit/{id_trans}")
def actualizar_nota(id_trans: int, nota: schema_devolucion.NotaFacturaCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Edita una nota credito existente (ver nota en crear_nota sobre el manejo de errores)."""
    db_actual = repository_devolucion.get_nota_by_id(db, id_trans=id_trans)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Nota credito no encontrada")
    if db_actual.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Nota credito no encontrada")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    nota.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_devolucion.update_nota(db=db, id_trans=id_trans, obj=nota)
    return {
        "status": "success",
        "message": "Nota crédito editada exitosamente",
        "data": None
    }


@router.delete("/delete/{id_trans}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_nota(id_trans: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina una nota credito (revierte su impacto en p_stock)."""
    db_actual = repository_devolucion.get_nota_by_id(db, id_trans=id_trans)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Nota credito no encontrada")
    if db_actual.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Nota credito no encontrada")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    repository_devolucion.delete_nota(db, id_trans=id_trans)
    return None
