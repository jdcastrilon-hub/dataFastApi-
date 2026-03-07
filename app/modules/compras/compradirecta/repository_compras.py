from sqlalchemy import desc, text
from sqlalchemy.orm import Session
from . import models, schema_compras 

def create_proveedor(db: Session, obj: schema_compras.CompraCreate):
    # Convertimos la lista de objetos LogEntry a una lista de diccionarios
    logs_dict = [log.model_dump() for log in obj.logs]
    # 1. Crear el objeto principal
    bd_compra = models.Compra(
        id_emp=obj.id_emp,
        id_proveedor=obj.id_proveedor,
        fec_doc =obj.fec_doc,
        documento=obj.documento,
        nro_docum=obj.nro_docum,
        remito= obj.remito,
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

    # 2. Crear las subcategorías vinculadas
    for i,det in enumerate(obj.detalles, start=1):
        de_detalles = models.DetalleCompra(            
            id_trans = bd_compra.id_trans,
            id_articulo = det.id_articulo,
            linea=i, #Numerador de linea
            #campos
            ref_compras = det.ref_compras,
            codigo_barras = det.codigo_barras,
            costo_unit = det.costo_unit,
            cantidad  = det.cantidad,
            id_lote = det.id_lote,
            stock = det.stock,
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

    db.flush() 
    db.commit()
    db.refresh(bd_compra)
    return bd_compra