from sqlalchemy import text
from sqlalchemy.orm import Session

from . import model_periodicidad


# Universo completo de periodicidades activas de la plataforma (para el picker
# de la pantalla Configuracion de Prestamos).
def get_todas(db: Session):
    return (
        db.query(model_periodicidad.Periodicidad)
        .filter(model_periodicidad.Periodicidad.activo == True)
        .order_by(model_periodicidad.Periodicidad.dias)
        .all()
    )


# Solo las periodicidades que la empresa activa tiene asignadas (opt-in via
# m_periodicidadxempresa) - es lo que consume el combo del formulario de
# Prestamo. JOIN por text() para no acoplar este catalogo al modulo confprestamo.
def get_habilitadas(db: Session, id_emp: int):
    return db.execute(
        text("""
            SELECT p.id, p.nombre, p.dias, p.observacion
            FROM public.m_periodicidad p
            INNER JOIN public.m_periodicidadxempresa pe
                ON pe.id_periodicidad = p.id AND pe.id_emp = :id_emp
            WHERE p.activo = true
            ORDER BY p.dias
        """),
        {"id_emp": id_emp}
    ).mappings().all()
