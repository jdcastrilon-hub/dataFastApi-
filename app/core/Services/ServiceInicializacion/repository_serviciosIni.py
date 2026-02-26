from sqlalchemy import desc, text
from sqlalchemy.orm import Session , joinedload
from . import schema_serviciosIni 

def NumeradorNext(db: Session,numerador : str):
    # Consulta nativa adaptada a SQLAlchemy
    query = text("""
        SELECT COALESCE((last_value + increment_by), 1) AS next_value
        FROM pg_sequences
        WHERE sequencename = :numerador
    """)
    
    return db.execute(query, {"numerador": numerador}).mappings().first()
   

def NumeradorNextReal(db: Session,numerador : str):
    # Consulta nativa adaptada a SQLAlchemy
    query = text("""
       SELECT nextval(:numerador) AS next_value
    """)
    
    return db.execute(query, {"numerador": numerador}).mappings().first().get("next_value")
   