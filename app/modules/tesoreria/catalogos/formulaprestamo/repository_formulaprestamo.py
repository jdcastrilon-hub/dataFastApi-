from sqlalchemy import text
from sqlalchemy.orm import Session

from . import model_formulaprestamo


# Universo completo de formulas activas de la plataforma (para el picker de la
# pantalla Configuracion de Prestamos).
def get_todas(db: Session):
    return (
        db.query(model_formulaprestamo.FormulaPrestamo)
        .filter(model_formulaprestamo.FormulaPrestamo.activo == True)
        .order_by(model_formulaprestamo.FormulaPrestamo.nombre)
        .all()
    )


# Solo las formulas que la empresa activa tiene asignadas (opt-in via
# m_formulaprestamoxempresa) - es lo que consume el combo del formulario de
# Prestamo. JOIN por text() para no acoplar este catalogo al modulo confprestamo.
def get_habilitadas(db: Session, id_emp: int):
    return db.execute(
        text("""
            SELECT f.id, f.codigo, f.nombre, f.genera_interes_mora
            FROM public.m_formulaprestamo f
            INNER JOIN public.m_formulaprestamoxempresa fe
                ON fe.id_formula = f.id AND fe.id_emp = :id_emp
            WHERE f.activo = true
            ORDER BY f.nombre
        """),
        {"id_emp": id_emp}
    ).mappings().all()
