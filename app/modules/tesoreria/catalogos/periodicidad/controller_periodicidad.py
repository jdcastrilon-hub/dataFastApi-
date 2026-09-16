from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_periodicidad, schema_periodicidad
from app.core.auth import security

# Catalogo GLOBAL de solo lectura: el mantenimiento del maestro (agregar una
# periodicidad nueva al universo) es a nivel plataforma (migracion / Postman),
# no hay pantalla CRUD ni MENU_CODIGO. Que periodicidades ve cada empresa se
# administra en /tesoreria/confprestamo.
router = APIRouter(
    prefix="/tesoreria/periodicidad",
    tags=["Tesoreria - Periodicidad"])


@router.get("/listAll", response_model=List[schema_periodicidad.PeriodicidadCombo])
def listar_todas(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Universo completo de periodicidades activas (picker de Configuracion de Prestamos)."""
    return repository_periodicidad.get_todas(db)


@router.get("/listCombo", response_model=List[schema_periodicidad.PeriodicidadCombo])
def listar_habilitadas(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Periodicidades asignadas a la empresa activa (combo del formulario de Prestamo)."""
    return repository_periodicidad.get_habilitadas(db, contexto.id_emp)
