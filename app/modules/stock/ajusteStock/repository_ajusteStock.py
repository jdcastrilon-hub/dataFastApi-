from sqlalchemy import desc, text
from sqlalchemy.orm import Session, joinedload
from . import models, schema_ajusteStock 

#Paginacion
def get_ajustes_paginated(db: Session, page: int, size: int):
    # 1. Contar el total de registros en la tabla
    total_records = db.query(models.AjusteStock).count()
    
    # 2. Obtener los registros de la página actual
    offset = page * size
    items = (
    db.query(models.AjusteStock)
    .options(
        joinedload(models.AjusteStock.bodega),
        joinedload(models.AjusteStock.estado),
        joinedload(models.AjusteStock.motivo))\
    .order_by(desc(models.AjusteStock.fecha_mod))
    .offset(offset)
    .limit(size)
    .all()
)
    
    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

# Obtener un ajuste por ID
def get_ajustestock(db: Session, id_trans: int): 
    return db.query(models.AjusteStock).filter(models.AjusteStock.id_trans == id_trans)\
                    .options(joinedload(models.AjusteStock.detalles)
                    .joinedload(models.DetalleAjusteStock.articulo)).first()

def create_ajustestock(db: Session, obj: schema_ajusteStock.AjusteStockCreate, nro_docum: int):
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        # 1. Crear el objeto principal
        bd_cabecera = models.AjusteStock(
            id_bodega=obj.id_bodega,
            documento=obj.documento,
            nro_docum=nro_docum,
            id_calculo=obj.id_calculo,
            fecha_movimiento=obj.fecha_movimiento,
            id_estado=obj.id_estado,
            id_motivo=obj.id_motivo,
            observacion=obj.observacion,
            vista=obj.vista,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_cabecera)
        db.flush() # Envio a base de datos

        # 2. Crear las subcategorías vinculadas
        for i,sub in enumerate(obj.detalles, start=1):
            db_sub = models.DetalleAjusteStock(
                id_trans=bd_cabecera.id_trans,
                id_articulo=sub.id_articulo,
                id_codbarra=sub.id_codbarra,
                linea=i, #Numerador de linea
                id_ubicacion=sub.id_ubicacion,
                id_lote=sub.id_lote,
                cant_disp=sub.cant_disp,
                cantidad=sub.cantidad
            )
            db.add(db_sub)
            
        db.flush() # Envio a base de datos

        # 3. LLAMAR AL STORED PROCEDURE (Antes del commit)
        # Usamos el ID que acabamos de generar
        db.execute(
            text("CALL public.sp_stock_impacto_AjusteStock(:operacion,:parm_trans)"), 
            {"operacion": "N", "parm_trans": bd_cabecera.id_trans}
        )   

        db.commit()
        db.refresh(bd_cabecera)

        return bd_cabecera
    
    except Exception as e:
            db.rollback() 
            raise e      