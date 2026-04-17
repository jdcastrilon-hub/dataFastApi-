from sqlalchemy import or_
from sqlalchemy.orm import Session
from . import modelo_personas 

# Obtener todas las bodegas ordenadas de mayor a menor
def get_personas(db: Session):
    return db.query(modelo_personas.Persona).all()


def find_persona_by_query(db: Session, query: str):
        # Creamos el patrón para el LIKE: %query%
        search_filter = f"%{query}%"
        
        return (
            db.query(
                modelo_personas.Persona.id_persona.label("idPersona"),
                modelo_personas.Persona.cod_tit.label("codTit"),
                modelo_personas.Persona.nombre_completo.label("nombreCompleto")
            )
            .filter(
                or_(
                    modelo_personas.Persona.cod_tit.ilike(search_filter),
                    modelo_personas.Persona.nombre_completo.ilike(search_filter)
                )
            )
            .order_by(modelo_personas.Persona.nombre_completo)
            .limit(20)
            .all()
        )
