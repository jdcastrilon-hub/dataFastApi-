from sqlalchemy import or_, desc
from sqlalchemy.orm import Session
from . import modelo_personas

def get_persona(db: Session, id_persona: int):
    return db.query(modelo_personas.Persona).filter(modelo_personas.Persona.id_persona == id_persona).first()


def find_persona_by_query(db: Session, id_emp: int, query: str):
        # Creamos el patrón para el LIKE: %query%
        search_filter = f"%{query}%"

        return (
            db.query(
                modelo_personas.Persona.id_persona.label("idPersona"),
                modelo_personas.Persona.cod_tit.label("codTit"),
                modelo_personas.Persona.nombre_completo.label("nombreCompleto")
            )
            .filter(
                modelo_personas.Persona.id_emp == id_emp,
                or_(
                    modelo_personas.Persona.cod_tit.ilike(search_filter),
                    modelo_personas.Persona.nombre_completo.ilike(search_filter)
                )
            )
            .order_by(modelo_personas.Persona.nombre_completo)
            .limit(20)
            .all()
        )


# Listado para el modal "Seleccionar persona" (Proveedores/Clientes): top N de
# la empresa activa, filtrable por documento o nombre - mismo patron de
# paginacion que el resto de los maestros del sistema.
def get_personas_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(modelo_personas.Persona).filter(modelo_personas.Persona.id_emp == id_emp)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                modelo_personas.Persona.cod_tit.ilike(patron),
                modelo_personas.Persona.nombre_completo.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query.order_by(desc(modelo_personas.Persona.fecha_mod)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }
