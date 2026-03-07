from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from . import model_sucursal, schema_sucursal
from app.modules.stock.bodegas import model_bodega

def get_sucursales(db: Session, page: int = 0, size: int = 100):
    print(page)
    return db.query(model_sucursal.Sucursal).offset(page).limit(size).all()


def get_sucursales_paginated(db: Session, page: int, size: int):
    total_records = db.query(model_sucursal.Sucursal).count()
    offset = page * size
    
    items = db.query(model_sucursal.Sucursal).offset(offset).limit(size).all()
    total_pages = (total_records + size - 1) // size if total_records > 0 else 0
    
    return {
        "items": items,
        "total_records": total_records,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": size
    }

def get_sucursales_by_bodegas(db: Session, id_empresa: int):
    # 1. Traemos las sucursales y cargamos sus bodegas relacionadas en una sola consulta
    sucursales = db.query(model_sucursal.Sucursal)\
        .options(joinedload(model_sucursal.Sucursal.bodegas))\
        .filter(model_sucursal.Sucursal.id_emp == id_empresa)\
        .all()

    # 2. Mapeamos directamente
    resultado = []
    for sucursal in sucursales:
        resultado.append({
            "id": sucursal.id,
            "idEmpresa": sucursal.id_emp,
            "codSucursal": sucursal.cod_sucursal,
            "nomSucursal": sucursal.nom_sucursal,
            "list_bodegas": sucursal.bodegas  # SQLAlchemy ya filtró esto por ti
        })
            
    return resultado

def create_sucursal(db: Session, sucursal: schema_sucursal.SucursalCreate):
    db_sucursal = model_sucursal.Sucursal(**sucursal.model_dump())
    db.add(db_sucursal)
    db.commit()
    db.refresh(db_sucursal)
    return db_sucursal