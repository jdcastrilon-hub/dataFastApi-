from fastapi import APIRouter, Depends, HTTPException, Response, status,Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_motivoajuste ,schema_ajuste
from app.modules.core.usuarios import model_usuario
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "INV_MOT"

router = APIRouter(
    prefix="/bodega/motivos",
    tags=["Bodega - Motivos"])

@router.get("/listCombo", response_model=List[schema_ajuste.MotivoCombo])
def listar_motivos(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Obtiene la lista de todos los motivos de la empresa."""
    return repository_motivoajuste.get_all(db, id_emp=contexto.id_emp)

@router.get("/pagination", response_model=schema_ajuste.PaginatedMotivoAjusteResponse)
def list_motivos_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    texto: str = Query(None),
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    return repository_motivoajuste.get_motivos_paginated(db, page, size, contexto.id_emp, texto)

@router.get("/search", response_model=schema_ajuste.MotivoAjusteResponse)
def obtener_motivo(id_motivo: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un motivo específico x ID."""
    db_motivo = repository_motivoajuste.get_motivo(db, id_motivo=id_motivo)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    return db_motivo

@router.post("/save")
def crear_motivo(motivo: schema_ajuste.MotivoAjusteCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Crea un nuevo motivo y retorna el objeto con su ID generado.
    No se atrapa la excepción aquí a propósito: así los errores de integridad
    (ej. codMotivo duplicado) los resuelve el manejador global de IntegrityError
    con un mensaje amigable, en una sola llamada."""
    motivo.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "CREAR")
    repository_motivoajuste.create_motivo(db=db, obj=motivo)
    return {
        "status": "success",
        "message": "Motivo creado exitosamente",
        "data": None
    }

@router.put("/edit")
def actualizar_motivo(id_motivo: int, motivo: schema_ajuste.MotivoAjusteCreate, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Actualiza los datos de un motivo existente."""
    db_motivo = repository_motivoajuste.get_motivo(db, id_motivo=id_motivo)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    if db_motivo.id_emp != contexto.id_emp:
        # No es de la empresa activa de la sesión: se trata como si no existiera
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")

    motivo.id_emp = contexto.id_emp  # ignora el id_emp que mande el cliente en el body
    repository_motivoajuste.update_motivo(db, id_motivo=id_motivo, obj=motivo)
    return {
        "status": "success",
        "message": "Motivo editado exitosamente",
        "data": None
    }

@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_motivo(id_motivo: int, db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Elimina un motivo del sistema."""
    db_motivo = repository_motivoajuste.get_motivo(db, id_motivo=id_motivo)
    if db_motivo is None:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    if db_motivo.id_emp != contexto.id_emp:
        raise HTTPException(status_code=404, detail="Motivo no encontrado")
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "ELIMINAR")
    repository_motivoajuste.delete_motivo(db, id_motivo=id_motivo)
    return None
