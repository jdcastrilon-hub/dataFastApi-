from fastapi import HTTPException
from sqlalchemy import desc, text
from sqlalchemy.orm import Session , joinedload
from . import models, schema_compras 

#Paginacion
def get_compras_paginated(db: Session, page: int, size: int,idempresa: int):
    # 1. Contar el total de registros en la tabla
    total_records = db.query(models.Compra).count()
    
    # 2. Obtener los registros de la página actual
    offset = page * size
    items = db.query(models.Compra)\
    .filter(models.Compra.id_emp == idempresa)\
    .options(
        joinedload(models.Compra.proveedor), 
        joinedload(models.Compra.bodega))\
    .offset(offset)\
    .limit(size)\
    .all()
    
    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

# Obtener una compra por ID 
def get_compras_by_id(db: Session, transaccion: int):
    return db.query(models.Compra).filter(models.Compra.id_trans == transaccion).options(
                    joinedload(models.Compra.bodega),
                    joinedload(models.Compra.nuevoCodigoBarra),
                    joinedload(models.Compra.detalles)
                    .joinedload(models.DetalleCompra.articulo)).first()

def consultar_stock_lote(db: Session, cadena: str, id_bodega: int, id_estado: int):
    """
    Llama a la función fn_compras_masivo_stock_costo de PostgreSQL 
    para obtener saldos y costos de múltiples artículos en una sola petición.
    """
    try:
        # 1. Definimos la consulta a la función
        # El orden de las columnas devueltas es: idArticulo, idCodBarra, stock, costo
        query = text("""
            SELECT idArticulo, idCodBarra, stock, costo 
            FROM public.compras_obtener_stock_costo_masivo(:cadena, :bodega, :estado)
        """)
        
        # 2. Ejecutamos pasando los parámetros
        result = db.execute(query, {
            "cadena": cadena, 
            "bodega": id_bodega, 
            "estado": id_estado
        })
        
        # 3. Mapeamos el resultado a una lista de diccionarios
        # Importante: Usamos nombres en CamelCase para que coincidan con tu Angular
        lista_actualizada = [
            {
                "idarticulo": row.idarticulo,
                "idcodbarra": row.idcodbarra,
                "stock": row.stock,
                "costo": float(row.costo) # Convertimos Decimal a float para el JSON
            }
            for row in result
        ]
        
        return lista_actualizada

    except Exception as e:
        # Log del error para depuración en Matrix
        print(f"Error en consultar_stock_lote: {str(e)}")
        return []

#Crear compras
def create_compra(db: Session, obj: schema_compras.CompraCreate, nro_docum : int) :
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        # 1. Crear el objeto principal
        bd_compra = models.Compra(
            id_emp=obj.id_emp,
            id_proveedor=obj.id_proveedor,
            fec_doc =obj.fec_doc,
            documento=obj.documento,
            nro_docum=nro_docum,
            remito= obj.remito,
            status=obj.status,
            ingresa_bodega= obj.ingresa_bodega,
            id_bodega =obj.id_bodega,
            id_estado =obj.id_estado,
            imp_neto =obj.imp_neto,
            imp_descuento =obj.imp_descuento,
            imp_total =obj.imp_total,
            observaciones = obj.observacion,
            impuesto1 = obj.impuesto1,
            valor_impuesto1 = obj.valor_impuesto1,
            impuesto2 = obj.impuesto2,
            valor_impuesto2 = obj.valor_impuesto2,
            impuesto3 = obj.impuesto3,
            valor_impuesto3 = obj.valor_impuesto3,
            vista = obj.vista,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_compra)
        db.flush() 

        # Insertar Detalles
        _procesar_detalles_y_codigos(db, bd_compra.id_trans, obj)        
        db.flush() # Envio a base de datos

        if(obj.status=='F'):
            # 3. LLAMAR AL STORED PROCEDURE (Antes del commit)
            # Usamos el ID que acabamos de generar
            db.execute(
                text("CALL public.sp_compradirecta(:operacion,:parm_trans)"), 
                {"operacion": "N", "parm_trans": bd_compra.id_trans}
            )   
        
        db.commit()
        db.refresh(bd_compra)
        return bd_compra

    except Exception as e:
        db.rollback() # ¡Fundamental! Deshace todo si algo falla
        raise HTTPException(status_code=400, detail=f"Error al crear la compra: {str(e)}")
    
# Actualizar Compra
def update_compra(db: Session, id_trans: int, obj: schema_compras.CompraCreate):
    try:
        # 1. Buscar la compra existente
        bd_compra = db.query(models.Compra).filter(models.Compra.id_trans == id_trans).first()
        if not bd_compra:
            raise HTTPException(status_code=404, detail="Compra no encontrada")

        # 2. Actualizar el objeto principal (Cabezal)
        # Seteamos los valores nuevos sobre el objeto recuperado
        bd_compra.id_proveedor = obj.id_proveedor
        bd_compra.fec_doc = obj.fec_doc
        bd_compra.remito = obj.remito
        bd_compra.status = obj.status
        bd_compra.id_bodega = obj.id_bodega
        bd_compra.id_estado = obj.id_estado
        bd_compra.imp_neto = obj.imp_neto
        bd_compra.imp_descuento = obj.imp_descuento
        bd_compra.imp_total = obj.imp_total
        bd_compra.observaciones = obj.observacion
        bd_compra.impuesto1 = obj.impuesto1
        bd_compra.valor_impuesto1 = obj.valor_impuesto1
        
        bd_compra.logs = [log.model_dump() for log in obj.logs]
        bd_compra.fecha_mod = obj.fecha_mod

        # ---------------------------------------------------------
        # 3. LIMPIEZA DE TABLAS HIJAS (Borrar para reinsertar)
        # ---------------------------------------------------------
        db.query(models.DetalleCompra).filter(models.DetalleCompra.id_trans == id_trans).delete()
        db.query(models.DetalleCompraNuevoCodigoBarra).filter(models.DetalleCompraNuevoCodigoBarra.id_trans == id_trans).delete()        
        db.flush() # Ejecuta los deletes pero mantiene la transacción abierta
       
        # Insertar Detalles
        _procesar_detalles_y_codigos(db, bd_compra.id_trans, obj)
        db.flush() # Envio a base de datos

        # 5. Lógica del Store Procedure para Edición
        if obj.status == 'F':
            # Llamamos al SP con operación 'E' (Edit) o la que maneje tu lógica de Matrix
            db.execute(
                text("CALL public.sp_compradirecta(:operacion, :parm_trans)"), 
                {"operacion": "N", "parm_trans": id_trans}
            )   
        
        db.commit()
        db.refresh(bd_compra)
        return bd_compra

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al editar la compra: {str(e)}")    
    

def _procesar_detalles_y_codigos(db: Session, id_trans: int, obj: schema_compras.CompraCreate):
        """
        Método privado para procesar e insertar detalles y nuevos códigos de barra.
        Reutilizado en Creación y Edición.
        """
        for i,det in enumerate(obj.detalles, start=1):
            de_detalles = models.DetalleCompra(            
                id_trans = id_trans,            
                linea=i, #Numerador de linea
                #campos
                id_articulo = det.id_articulo,
                id_codbarra  = det.id_codbarra,
                ref_compras = det.ref_compras,
                costo_unit = det.costo_unit,
                cantidad  = det.cantidad,
                id_lote = det.id_lote,
                stock = det.stock,
                porc_dcto = det.porc_dcto,
                imp_dcto = det.imp_dcto,
                impuesto1 = det.impuesto1,
                id_tasaimp1 = det.id_tasaimp1,
                valor_impuesto1 = det.valor_impuesto1,
                impuesto2 = det.impuesto2,
                id_tasaimp2 = det.id_tasaimp2,
                valor_impuesto2 = det.valor_impuesto2,
                impuesto3 = det.impuesto3,
                id_tasaimp3 = det.id_tasaimp3,
                valor_impuesto3 = det.valor_impuesto3,
                costo_total = det.costo_total,
                importe = det.importe
            )
            db.add(de_detalles)
            

        # 3. Crear nuevos codigos de barra si es necesario
        for i,newcodigos in enumerate(obj.nuevoCodigoBarra, start=1):
            de_detalle_nuevoscodigos = models.DetalleCompraNuevoCodigoBarra( 
                id_trans = id_trans,
                id_articulo = newcodigos.id_articulo,
                id_codbarra = newcodigos.id_codbarra,
                linea=i, #Numerador de linea
                #Campos
                cod_barra = newcodigos.cod_barra,
                ref_barra=newcodigos.ref_barra
            )
            db.add(de_detalle_nuevoscodigos)