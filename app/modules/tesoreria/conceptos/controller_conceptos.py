from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from . import schema_conceptos, repository_conceptos
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/tesoreria/conceptos",
    tags=["tesoreria - Conceptos"])

@router.get("/porusuario", response_model=list[schema_conceptos.ConceptoCombo])
def conceptos_por_usuario(
    id_usuario: int,
    idempresa: int,
    signo: int,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Conceptos activos asociados al usuario, filtrados por signo (1=Ingreso/
    -1=Gasto) - usado por Movimiento Caja (comercial)."""
    return repository_conceptos.get_conceptos_por_usuario(db, id_usuario=id_usuario, idempresa=idempresa, signo=signo)

#Buscar concepto por ID
@router.get("/search", response_model=schema_conceptos.ConceptoBase)
def obtener_concepto(id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Busca un concepto específico x ID."""
    bd_concepto = repository_conceptos.get_concepto_by_id(db, id=id)
    if bd_concepto is None:
        raise HTTPException(status_code=404, detail="Concepto no encontrado")
    return bd_concepto

@router.get("/pagination", response_model=schema_conceptos.PaginatedConceptoResponse)
def list_conceptos_paginacion(
    page: int = Query(0, ge=0),
    size: int = Query(10, ge=1),
    idempresa: int = 1,
    texto: str = Query(None),
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    return repository_conceptos.get_conceptos_paginated(db, page, size, idempresa, texto)

@router.post("/save")
def crear_concepto(concepto: schema_conceptos.ConceptoCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un nuevo Concepto. No se atrapa la excepcion aqui a proposito: los errores
    de integridad los resuelve el manejador global con un mensaje amigable."""
    repository_conceptos.create_concepto(db=db, obj=concepto)
    return {
            "status": "success",
            "message": "Concepto creado exitosamente",
            "data": None
    }

@router.put("/edit/{id}")
def actualizar_concepto(id: int, concepto: schema_conceptos.ConceptoCreate, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Editar un concepto."""
    repository_conceptos.update_concepto(db=db, id=id, obj=concepto)
    return {
        "status": "success",
        "message": "Concepto editado exitosamente",
        "data": None
    }

@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_concepto(id: int, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Elimina un concepto del sistema."""
    success = repository_conceptos.delete_concepto(db, id=id)
    if not success:
        raise HTTPException(status_code=404, detail="Concepto no encontrado")
    return None
