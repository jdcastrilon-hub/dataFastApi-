from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_ajusteprecio, schema_ajusteprecio
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/ajusteprecio",
    tags=["comercial - Ajuste Precio"])


@router.post("/save")
def save(ajuste: schema_ajusteprecio.AjustePrecioBase, db: Session = Depends(get_db), usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Crea un ajuste de precio manual. No se atrapa la excepcion aqui a
    proposito: los errores de integridad los resuelve el manejador global."""
    repository_ajusteprecio.create_ajuste(db=db, obj=ajuste)
    return {
        "status": "success",
        "message": "Ajuste de precio aplicado exitosamente",
        "data": None
    }
