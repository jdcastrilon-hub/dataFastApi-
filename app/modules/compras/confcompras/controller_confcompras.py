from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_confcompras, schema_confcompras
from app.core.auth import security

router = APIRouter(
    prefix="/compras/confcompras",
    tags=["Compras - Configuracion"])


@router.get("/search", response_model=schema_confcompras.ConfComprasBase)
def obtener_confcompras(
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Configuracion de compras de la empresa activa. Es un singleton por
    empresa - si todavia no se ha guardado ninguna, devuelve los valores por
    defecto (deny by default) en vez de un 404."""
    db_conf = repository_confcompras.get_confcompras(db, contexto.id_emp)

    if db_conf is None:
        return schema_confcompras.ConfComprasBase(idEmp=contexto.id_emp)

    return schema_confcompras.ConfComprasBase.model_validate(db_conf)


@router.put("/save")
def guardar_confcompras(
    obj: schema_confcompras.ConfComprasBase,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Guarda la configuracion de compras (single round-trip)."""
    repository_confcompras.upsert_confcompras(db, contexto.id_emp, obj)
    return {
        "status": "success",
        "message": "Configuracion de compras guardada exitosamente",
        "data": None
    }
