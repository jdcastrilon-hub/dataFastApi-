from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from . import repository_formulaprestamo, schema_formulaprestamo
from app.core.auth import security

# Catalogo GLOBAL de solo lectura: el mantenimiento del maestro (agregar una
# formula nueva al universo) es a nivel plataforma (migracion / Postman) y
# ademas requiere codigo que ramifique en la logica de calculo. No hay pantalla
# CRUD ni MENU_CODIGO. Que formulas ve cada empresa se administra en
# /tesoreria/confprestamo.
router = APIRouter(
    prefix="/tesoreria/formulaprestamo",
    tags=["Tesoreria - Formula de Prestamo"])


@router.get("/listAll", response_model=List[schema_formulaprestamo.FormulaPrestamoCombo])
def listar_todas(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Universo completo de formulas activas (picker de Configuracion de Prestamos)."""
    return repository_formulaprestamo.get_todas(db)


@router.get("/listCombo", response_model=List[schema_formulaprestamo.FormulaPrestamoCombo])
def listar_habilitadas(db: Session = Depends(get_db), contexto: security.ContextoUsuario = Depends(security.obtener_contexto_actual)):
    """Formulas asignadas a la empresa activa (combo del formulario de Prestamo)."""
    return repository_formulaprestamo.get_habilitadas(db, contexto.id_emp)
