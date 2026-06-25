from sqlalchemy import and_, desc
from sqlalchemy.orm import Session, contains_eager, joinedload
from . import model_sucursal, schema_sucursal
from app.modules.stock.bodegas import model_bodega
from app.modules.comercial.documentos import model_docum
from app.modules.comercial.mediopago import model_medio
from app.modules.comercial.cajas import model_cajas

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
    
    mediopago = db.query(model_medio.MedioPago).order_by(model_medio.MedioPago.orden).all()
    
    # 2. Mapeamos directamente
    resultado = []
    for sucursal in sucursales:
        #Documentos de la empresa y sucursal
        documentos = db.query(model_docum.DocumentoVenta)\
        .filter(model_docum.DocumentoVenta.id_emp == id_empresa,
                model_docum.DocumentoVenta.id_sucursal_emp == sucursal.id)\
        .all()

        

        resultado.append({
            "id": sucursal.id,
            "idEmpresa": sucursal.id_emp,
            "codSucursal": sucursal.cod_sucursal,
            "nomSucursal": sucursal.nom_sucursal,
            "list_bodegas": sucursal.bodegas,
            "documentos":documentos,
            "mediopago":mediopago
        })
            
    return resultado


def get_sucursales_by_cajas(db: Session, id_empresa: int):

    sucursales = (
            db.query(model_sucursal.Sucursal)
            # 1. Aquí haces el JOIN usando la relación de tu modelo
            .join(model_sucursal.Sucursal.caja)
            # 2. Le indicas a SQLAlchemy que use este mismo JOIN para mapear los objetos hijos
            .options(contains_eager(model_sucursal.Sucursal.caja))
            # 3. Aplicas los filtros usando directamente la clase del modelo de la caja (MCaja)
            .filter(
                and_(
                    model_sucursal.Sucursal.id_emp == id_empresa,
                    model_sucursal.Sucursal.activo == "S",
                    # CORRECCIÓN: Usamos la clase MCaja directamente. 
                    # SQLAlchemy es inteligente y sabe que se refiere al JOIN de arriba.
                    model_cajas.MCaja.cajapos == True  
                )
            )
            .all()
        )
    
   # Mapeamos manualmente el atributo de la relación si el nombre difiere.
    # En tu modelo pusiste: caja = relationship("MCaja", back_populates="sucursal")
    # Pero el JSON espera la propiedad llamada 'cajas'. Hacemos el mapeo rápido:
    for s in sucursales:
        s.cajas = s.caja  # Asignamos la lista de MCaja al atributo virtual 'cajas' que pide Pydantic
        
    return sucursales

def create_sucursal(db: Session, sucursal: schema_sucursal.SucursalCreate):
    db_sucursal = model_sucursal.Sucursal(**sucursal.model_dump())
    db.add(db_sucursal)
    db.commit()
    db.refresh(db_sucursal)
    return db_sucursal