from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from . import repository_confprestamo, schema_confprestamo
from app.core.auth import security
from app.core.auth.permisos import verificar_permiso

# Codigo del formulario en md_menu (matriz de permisos)
MENU_CODIGO = "TES_CONFPREST"

router = APIRouter(
    prefix="/tesoreria/confprestamo",
    tags=["Tesoreria - Configuracion de Prestamos"])


@router.get("/search", response_model=schema_confprestamo.ConfPrestamoBase)
def obtener_confprestamo(
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Que periodicidades / formulas tiene asignadas la empresa activa, mas el
    universo completo de ambos catalogos para pintar las casillas. Singleton por
    empresa: si no se ha configurado nada, los habilitados salen vacios."""
    return repository_confprestamo.get_confprestamo(db, contexto.id_emp)


@router.put("/save")
def guardar_confprestamo(
    obj: schema_confprestamo.ConfPrestamoBase,
    db: Session = Depends(get_db),
    contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Guarda las dos grillas completas (periodicidades + formulas de la empresa)
    en una sola llamada. Un id inexistente lo rechaza la FK via el handler
    global de IntegrityError (sin endpoint de validacion previa)."""
    verificar_permiso(db, contexto.usuario.id_usuario, contexto.id_emp, MENU_CODIGO, "EDITAR")
    repository_confprestamo.upsert_confprestamo(db, contexto.id_emp, obj)
    return {
        "status": "success",
        "message": "Configuracion de prestamos guardada exitosamente",
        "data": None
    }
