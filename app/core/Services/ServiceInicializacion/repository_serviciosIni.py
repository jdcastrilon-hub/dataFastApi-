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

def get_compra_disponible(db: Session, id_articulo: int,id_codbarra: int, bodega_id: int, estado_id: int , id_proveedor : int):
        # Definimos el query nativo llamando a la función
        query = text("""
            SELECT 
                s.stock AS "stock", 
                s.costo AS "costo"
            FROM comprasdisponiblexbodega(:param_articulo_id, :param_id_codbarra, :param_bodega_id, :param_estado_id, :param_id_proveedor) AS s
        """)
        
        # Ejecutamos con los parámetros
        result = db.execute(query, {
            "param_articulo_id" :id_articulo,
            "param_id_codbarra": id_codbarra,
            "param_bodega_id": bodega_id,
            "param_estado_id": estado_id,
            "param_id_proveedor": id_proveedor
        })
        
        # Convertimos los resultados a diccionarios para que Pydantic los valide
        return result.mappings().all()
   