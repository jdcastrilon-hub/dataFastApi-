from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_compras, schema_compras
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/compras/compradirecta",
    tags=["Compras - Proveedor"])

#Buscar Compras por ID
@router.get("/search", response_model=schema_compras.CompraBase)
def obtener_compra(transaccion: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca una compra específica x ID."""
    bd_compra = repository_compras.get_compras_by_id(db, transaccion=transaccion)
    if bd_compra is None or bd_compra.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    return bd_compra

@router.get("/pagination", response_model=schema_compras.PaginatedCompraResponse)
def list_bodegas_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_compras.get_compras_paginated(db, page, size, contexto.id_emp, texto)

@router.post("/save")
def crear_compra(compra: schema_compras.CompraCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea una nueva compra y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores del SP o de integridad
    los resuelve el manejador global correspondiente (TransaccionValidationError/IntegrityError)
    con un mensaje amigable, en una sola llamada."""
    compra.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_compras.create_compra(db=db, obj=compra)
    return {
        "status": "success",
        "message": "Compra creada exitosamente",
        "data": None
    }

@router.put("/edit/{id_trans}")
def actualizar_compra(id_trans: int,compra: schema_compras.CompraCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Editar una compra y retorna el objeto con su ID generado (ver nota en crear_compra sobre el manejo de errores)."""
    db_actual = repository_compras.get_compras_by_id(db, transaccion=id_trans)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    if db_actual.id_emp != contexto.id_emp:
        # No es de la empresa activa de la sesión: se trata como si no existiera
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    compra.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_compras.update_compra(db=db,id_trans=id_trans, obj=compra)
    return {
        "status": "success",
        "message": "Compra editada exitosamente",
        "data": None
    }

@router.delete("/delete/{id_trans}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_compra(id_trans: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina una compra del sistema."""
    db_actual = repository_compras.get_compras_by_id(db, transaccion=id_trans)
    if db_actual is None:
        raise HTTPException(status_code=404, detail="Compra no encontrada")
    if db_actual.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Compra no encontrada")

    repository_compras.delete_compra(db, id_trans=id_trans)
    return None

@router.get("/stock-masivo", response_model=List[schema_compras.CompraActualizacionDatos])
def get_stock_masivo(cadena: str, id_bodega: int, id_estado: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_compras.consultar_stock_lote(db, cadena, id_bodega, id_estado)