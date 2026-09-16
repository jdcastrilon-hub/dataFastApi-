from sqlalchemy import text
from sqlalchemy.orm import Session

from app.modules.tesoreria.catalogos.periodicidad import repository_periodicidad
from app.modules.tesoreria.catalogos.formulaprestamo import repository_formulaprestamo
from . import schema_confprestamo


def get_confprestamo(db: Session, id_emp: int) -> schema_confprestamo.ConfPrestamoBase:
    """Arma el DTO de la pantalla: universo completo de catalogos + ids que la
    empresa activa tiene asignados. Si la empresa no ha configurado nada, las
    listas de habilitados salen vacias (nunca 404 - mismo criterio que
    get_confcomercial)."""
    periodicidades = db.execute(
        text("SELECT id_periodicidad FROM public.m_periodicidadxempresa WHERE id_emp = :id_emp"),
        {"id_emp": id_emp}
    ).scalars().all()

    formulas = db.execute(
        text("SELECT id_formula FROM public.m_formulaprestamoxempresa WHERE id_emp = :id_emp"),
        {"id_emp": id_emp}
    ).scalars().all()

    return schema_confprestamo.ConfPrestamoBase(
        periodicidadesHabilitadas=list(periodicidades),
        formulasHabilitadas=list(formulas),
        catalogoPeriodicidades=[
            schema_confprestamo.PeriodicidadCombo.model_validate(p)
            for p in repository_periodicidad.get_todas(db)
        ],
        catalogoFormulas=[
            schema_confprestamo.FormulaPrestamoCombo.model_validate(f)
            for f in repository_formulaprestamo.get_todas(db)
        ],
    )


# Borrar-e-reinsertar la grilla completa en una sola transaccion (single
# round-trip). Un id que no exista en la maestra revienta la FK -> lo traduce
# el handler global de IntegrityError, sin pre-validacion aparte.
def upsert_confprestamo(db: Session, id_emp: int, obj: schema_confprestamo.ConfPrestamoBase):
    db.execute(
        text("DELETE FROM public.m_periodicidadxempresa WHERE id_emp = :id_emp"),
        {"id_emp": id_emp}
    )
    db.execute(
        text("DELETE FROM public.m_formulaprestamoxempresa WHERE id_emp = :id_emp"),
        {"id_emp": id_emp}
    )

    for id_periodicidad in dict.fromkeys(obj.periodicidades_habilitadas):
        db.execute(
            text("""
                INSERT INTO public.m_periodicidadxempresa (id_emp, id_periodicidad)
                VALUES (:id_emp, :id_periodicidad)
            """),
            {"id_emp": id_emp, "id_periodicidad": id_periodicidad}
        )

    for id_formula in dict.fromkeys(obj.formulas_habilitadas):
        db.execute(
            text("""
                INSERT INTO public.m_formulaprestamoxempresa (id_emp, id_formula)
                VALUES (:id_emp, :id_formula)
            """),
            {"id_emp": id_emp, "id_formula": id_formula}
        )

    db.commit()
