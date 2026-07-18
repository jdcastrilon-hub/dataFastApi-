from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_numerador
from app.modules.core.usuarios import model_usuario
from app.core.auth import security

router = APIRouter(
    prefix="/core/numeradores",
    tags=["Core - Numeradores"])

@router.get("/preview")
def previsualizar_numerador(
    id_emp: int,
    codigo: str,
    db: Session = Depends(get_db),
    usuario_autenticado: model_usuario.Usuario = Depends(security.obtener_usuario_actual)):
    """Devuelve el siguiente consecutivo tentativo para (id_emp, codigo) SIN
    consumirlo - ver la nota en repository_numerador.previsualizar_numerador."""
    valor = repository_numerador.previsualizar_numerador(db, id_emp=id_emp, codigo=codigo)
    return {"next_value": valor}
