from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_motivodevolucion, schema_motivodevolucion
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/compras/motivosdevolucion",
    tags=["Compras - Motivos Devolucion"])

@router.get("/listCombo", response_model=List[schema_motivodevolucion.MotivoDevolucionCombo])
def listar_motivos(id_emp: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Obtiene la lista de todos los motivos de devolucion de la empresa."""
    return repository_motivodevolucion.get_all(db, id_emp=id_emp)

@router.get("/pagination", response_model=schema_motivodevolucion.PaginatedMotivoDevolucionResponse)
def list_motivos_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    id_emp: int = 0,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_motivodevolucion.get_motivos_paginated(db, page, size, id_emp, texto)

@router.get("/search", response_model=schema_motivodevolucion.MotivoDevolucionResponse)
def obtener_motivo(id_motivo: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un motivo de devolucion especifico x ID."""
    db_motivo = repository_motivodevolucion.get_motivo(db, id_motivo=id_motivo)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    return db_motivo

@router.post("/save")
def crear_motivo(motivo: schema_motivodevolucion.MotivoDevolucionCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo motivo de devolucion y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    (ej. codMotivo duplicado) los resuelve el manejador global de IntegrityError
    con un mensaje amigable, en una sola llamada."""
    repository_motivodevolucion.create_motivo(db=db, obj=motivo)
    return {
        "status": "success",
        "message": "Motivo creado exitosamente",
        "data": None
    }

@router.put("/edit")
def actualizar_motivo(id_motivo: int, motivo: schema_motivodevolucion.MotivoDevolucionCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Actualiza los datos de un motivo de devolucion existente."""
    db_motivo = repository_motivodevolucion.get_motivo(db, id_motivo=id_motivo)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")

    repository_motivodevolucion.update_motivo(db, id_motivo=id_motivo, obj=motivo)
    return {
        "status": "success",
        "message": "Motivo editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_motivo(id_motivo: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina un motivo de devolucion del sistema."""
    success = repository_motivodevolucion.delete_motivo(db, id_motivo=id_motivo)
    if not success:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    return None
