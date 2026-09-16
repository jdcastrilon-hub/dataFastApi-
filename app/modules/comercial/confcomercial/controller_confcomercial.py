from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_confcomercial, schema_confcomercial
from app.core.auth import security

router = APIRouter(
    prefix="/comercial/confcomercial",
    tags=["Comercial - Configuracion"])


@router.get("/search", response_model=schema_confcomercial.ConfComercialBase)
def obtener_confcomercial(
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Configuracion comercial de la empresa activa. Es un singleton por
    empresa - si todavia no se ha guardado ninguna, devuelve los valores
    por defecto (deny by default) en vez de un 404."""
    db_conf = repository_confcomercial.get_confcomercial(db, contexto.id_emp)
    roles = repository_confcomercial.get_roles_descuento(db, contexto.id_emp)
    roles_dto = [schema_confcomercial.DctoRolBase.model_validate(r) for r in roles]

    if db_conf is None:
        return schema_confcomercial.ConfComercialBase(
            idEmp=contexto.id_emp,
            rolesDescuento=roles_dto
        )

    data = schema_confcomercial.ConfComercialBase.model_validate(db_conf)
    data.roles_descuento = roles_dto
    return data


@router.put("/save")
def guardar_confcomercial(
    obj: schema_confcomercial.ConfComercialBase,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Guarda la configuracion comercial y la grilla completa de roles con
    descuento en una sola llamada (single round-trip)."""
    repository_confcomercial.upsert_confcomercial(db, contexto.id_emp, obj)
    return {
        "status": "success",
        "message": "Configuracion comercial guardada exitosamente",
        "data": None
    }
