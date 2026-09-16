from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_motivodevolucionventa, schema_motivodevolucionventa
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

MENU_CODIGO = "VEN_MOTIVO"

router = APIRouter(
    prefix="/comercial/motivosdevolucionventa",
    tags=["Comercial - Motivos Devolucion Venta"])


@router.get("/listCombo", response_model=List[schema_motivodevolucionventa.MotivoDevolucionVentaCombo])
def listar_motivos(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Obtiene la lista de todos los motivos de devolucion de venta de la empresa."""
    return repository_motivodevolucionventa.get_all(db, id_emp=contexto.id_emp)


@router.get("/pagination", response_model=schema_motivodevolucionventa.PaginatedMotivoDevolucionVentaResponse)
def list_motivos_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_motivodevolucionventa.get_motivos_paginated(db, page, size, contexto.id_emp, texto)


@router.get("/search", response_model=schema_motivodevolucionventa.MotivoDevolucionVentaResponse)
def obtener_motivo(id_motivo: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Busca un motivo de devolucion de venta especifico x ID."""
    db_motivo = repository_motivodevolucionventa.get_motivo(db, id_motivo=id_motivo)
    if db_motivo is None or db_motivo.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    return db_motivo


@router.post("/save")
def crear_motivo(motivo: schema_motivodevolucionventa.MotivoDevolucionVentaCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea un nuevo motivo de devolucion de venta. No se atrapa la excepcion
    aqui a proposito: los errores de integridad (ej. codMotivo duplicado) los
    resuelve el manejador global con un mensaje amigable."""
    motivo.id_emp = contexto.id_emp
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_motivodevolucionventa.create_motivo(db=db, obj=motivo)
    return {
        "status": "success",
        "message": "Motivo creado exitosamente",
        "data": None
    }


@router.put("/edit")
def actualizar_motivo(id_motivo: int, motivo: schema_motivodevolucionventa.MotivoDevolucionVentaCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos de un motivo de devolucion de venta existente."""
    db_motivo = repository_motivodevolucionventa.get_motivo(db, id_motivo=id_motivo)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    if db_motivo.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    motivo.id_emp = contexto.id_emp
    repository_motivodevolucionventa.update_motivo(db, id_motivo=id_motivo, obj=motivo)
    return {
        "status": "success",
        "message": "Motivo editado exitosamente",
        "data": None
    }


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_motivo(id_motivo: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina un motivo de devolucion de venta del sistema."""
    db_motivo = repository_motivodevolucionventa.get_motivo(db, id_motivo=id_motivo)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    if db_motivo.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")

    repository_motivodevolucionventa.delete_motivo(db, id_motivo=id_motivo)
    return None
