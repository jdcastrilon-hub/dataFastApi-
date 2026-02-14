from sqlalchemy.orm import Session
from . import model_pais, schemas

def get_paises(db: Session):
    # Equivale a: SELECT * FROM public.m_pais
    return db.query(model_pais.model_pais).all()

def create_pais(db: Session, pais: schemas.PaisCreate):
    db_pais = model_pais.model_pais(cod_pais=pais.cod_pais, nom_pais=pais.nom_pais)
    db.add(db_pais)
    db.commit()
    db.refresh(db_pais)
    return db_pais