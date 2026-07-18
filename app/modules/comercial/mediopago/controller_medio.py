from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import respository_medio, schema_medio
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/mediopago",
    tags=["Comercial - MedioPago"])

@router.get("/list", response_model=List[schema_medio.MedioPagoCombo])
def search_medios_pago(db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return respository_medio.get_medios_pago(db)

@router.get("/pagination", response_model=schema_medio.PaginatedMedioPagoResponse)
def list_medios_pago_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa: int = Query(...),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return respository_medio.get_medios_pago_paginated(db, page, size, idempresa, texto)

#Buscar medio de pago por ID
@router.get("/search", response_model=schema_medio.MedioPagoBase)
def obtener_medio_pago(id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un medio de pago específico x ID."""
    bd_medio = respository_medio.get_medio_pago_by_id(db, id=id)
    if bd_medio is None:
        raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
    return bd_medio

@router.post("/save")
def crear_medio_pago(medio: schema_medio.MedioPagoCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo medio de pago. No se atrapa la excepcion aqui a proposito: un
    tipo duplicado para la misma empresa (UNIQUE id_emp+tipo) lo resuelve el
    manejador global de IntegrityError con un mensaje amigable, sin endpoint de
    validacion previa (ver feedback_data_single_roundtrip)."""
    respository_medio.create_medio_pago(db=db, obj=medio)
    return {
            "status": "success",
            "message": "Medio de pago creado exitosamente",
            "data": None
    }

@router.put("/edit/{id}")
def actualizar_medio_pago(id: int, medio: schema_medio.MedioPagoCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Editar un medio de pago (ver nota en crear_medio_pago sobre el manejo de errores)."""
    db_medio = respository_medio.update_medio_pago(db, id=id, obj=medio)
    if db_medio is None:
        raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
    return {
        "status": "success",
        "message": "Medio de pago editado exitosamente",
        "data": None
    }

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_medio_pago(id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina un medio de pago del sistema."""
    success = respository_medio.delete_medio_pago(db, id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Medio de pago no encontrado")
    return None
