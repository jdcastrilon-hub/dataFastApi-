from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import String, cast, desc, or_, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session , joinedload

from app.exceptions import TransaccionValidationError
from app.modules.comercial.clientes import model_cliente
from . import models_ventas, schema_ventas


#Paginacion
def get_ventas_paginated(db: Session, page: int, size: int, idempresa: int, texto: str = None, vista: str = None):
    query = db.query(models_ventas.Factura).filter(models_ventas.Factura.id_emp == idempresa)

    # venta-directa y venta-pos comparten tabla (t_facturas) pero son pantallas
    # distintas - se distinguen por el campo 'vista' ('VentaDirect'/'VentaPOS').
    if vista:
        query = query.filter(models_ventas.Factura.vista == vista)

    # Filtro de busqueda por nro. de documento o nombre del cliente
    if texto:
        patron = f"%{texto}%"
        query = query\
            .join(models_ventas.Factura.cliente)\
            .filter(
                or_(
                    cast(models_ventas.Factura.nro_docum, String).ilike(patron),
                    model_cliente.Cliente.nom_cliente.ilike(patron)
                )
            )

    total_records = query.count()

    offset = page * size
    items = query\
        .options(
            joinedload(models_ventas.Factura.cliente),
            joinedload(models_ventas.Factura.bodega))\
        .order_by(desc(models_ventas.Factura.fecha_mod))\
        .offset(offset)\
        .limit(size)\
        .all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

# Obtener una venta por ID
def get_venta_by_id(db: Session, id_trans: int, id_emp: int):
    return db.query(models_ventas.Factura).filter(
        models_ventas.Factura.id_trans == id_trans,
        models_ventas.Factura.id_emp == id_emp
    ).options(
        joinedload(models_ventas.Factura.cliente),
        joinedload(models_ventas.Factura.bodega),
        joinedload(models_ventas.Factura.detalles),
        joinedload(models_ventas.Factura.detalles_pago).joinedload(models_ventas.FacturaMedioPago.mediopago)
    ).first()

def _validar_detalles_pago(obj: schema_ventas.ventaCreate):
    """La suma de las lineas de pago (uno o varios medios) debe cuadrar
    exactamente con el total de la venta - sin esto se podria grabar una
    venta cuyo dinero registrado no coincide con lo realmente cobrado."""
    if not obj.detalles_pago:
        raise HTTPException(status_code=400, detail="Debe indicar al menos un medio de pago.")
    suma = sum((d.importe for d in obj.detalles_pago), Decimal("0"))
    if abs(suma - obj.imp_total) > Decimal("0.01"):
        raise HTTPException(
            status_code=400,
            detail=f"La suma de los medios de pago (${suma}) no coincide con el total de la venta (${obj.imp_total})."
        )

#Crear venta
def create_venta(db: Session, obj: schema_ventas.ventaCreate, nro_docum : int) :
    _validar_detalles_pago(obj)
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        # 1. Crear el objeto principal
        bd_venta = models_ventas.Factura(
            id_emp=obj.id_emp,
            id_cliente=obj.id_cliente,
            id_sucursal_cliente=1,
            id_sucursal_emp=obj.id_sucursal_emp,
            id_bodega =obj.id_bodega,

            fec_doc =obj.fec_doc,
            documento=obj.documento,
            nro_docum=nro_docum,
            serie_docum=obj.serie_docum,

            documento_ref="",            
            nro_ref=0,            
            serie_ref="",              
            documento_remito="",            
            nro_remito=0,            
            serie_remito="", 
            id_turno=obj.id_turno,
            id_caja=obj.id_caja,
            id_lista=obj.id_lista,

            observacion = obj.observacion,
            imp_ingreso = obj.imp_ingreso,
            imp_vuelto = obj.imp_vuelto,
            fec_venc= obj.fec_doc,
            id_moneda=1,       
            id_estado =obj.id_estado,
            vista = obj.vista,
            signo=1,

            imp_neto =obj.imp_neto,
            tipo_dcto = obj.tipo_dcto,
            porc_dcto= obj.porc_dcto,
            imp_descuento =obj.imp_descuento,
            imp_total =obj.imp_total,
            
            impuesto1 = obj.impuesto1,
            valor_impuesto1 = obj.valor_impuesto1,
            impuesto2 = obj.impuesto2,
            valor_impuesto2 = obj.valor_impuesto2,
            impuesto3 = obj.impuesto3,
            valor_impuesto3 = obj.valor_impuesto3,
            
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_venta)
        db.flush() 

         # Insertar Detalles
        _procesar_detalles(db, bd_venta.id_trans,bd_venta.id_emp, obj)
        _procesar_detalles_pago(db, bd_venta.id_trans, bd_venta.id_emp, obj)
        db.flush() # Envio a base de datos

        db.execute(
                text("CALL public.sp_comercial_ventapos(:operacion,:parm_trans)"), 
                {"operacion": "N", "parm_trans": bd_venta.id_trans}
            ) 

        #Control de transaccion
        db.execute(
                text("CALL public.sp_general_control_transacciones(:parm_trans)"), 
                {"parm_trans": bd_venta.id_trans}
            )     

        
        db.commit()
        db.refresh(bd_venta)
        return bd_venta

    except (IntegrityError, DataError):
        # No se envuelve: se deja que el manejador global responda con el mensaje
        # amigable especifico (mismo motivo que en repository_compras.create_compra).
        db.rollback()
        raise
    except Exception as e:
        # Errores de negocio lanzados por los SPs (ej. sp_general_control_stock),
        # no violaciones de integridad - esas ya se filtraron arriba.
        db.rollback() # ¡Fundamental! Deshace todo si algo falla
        raise TransaccionValidationError(str(e.orig))


# Actualizar venta (misma limitacion conocida que update_compra: no revierte el
# impacto en stock/costos de la version anterior antes de volver a llamar al SP,
# ver project_data_comercial_module / project_data_crud_template).
def update_venta(db: Session, id_trans: int, id_emp: int, obj: schema_ventas.ventaCreate):
    _validar_detalles_pago(obj)
    try:
        bd_venta = db.query(models_ventas.Factura).filter(
            models_ventas.Factura.id_trans == id_trans,
            models_ventas.Factura.id_emp == id_emp
        ).first()
        if not bd_venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")

        bd_venta.id_cliente = obj.id_cliente
        bd_venta.id_sucursal_emp = obj.id_sucursal_emp
        bd_venta.id_bodega = obj.id_bodega
        bd_venta.fec_doc = obj.fec_doc
        bd_venta.id_turno = obj.id_turno
        bd_venta.id_caja = obj.id_caja
        bd_venta.id_lista = obj.id_lista
        bd_venta.observacion = obj.observacion
        bd_venta.imp_ingreso = obj.imp_ingreso
        bd_venta.imp_vuelto = obj.imp_vuelto
        bd_venta.id_estado = obj.id_estado
        bd_venta.imp_neto = obj.imp_neto
        bd_venta.tipo_dcto = obj.tipo_dcto
        bd_venta.porc_dcto = obj.porc_dcto
        bd_venta.imp_descuento = obj.imp_descuento
        bd_venta.imp_total = obj.imp_total
        bd_venta.impuesto1 = obj.impuesto1
        bd_venta.valor_impuesto1 = obj.valor_impuesto1
        bd_venta.impuesto2 = obj.impuesto2
        bd_venta.valor_impuesto2 = obj.valor_impuesto2
        bd_venta.impuesto3 = obj.impuesto3
        bd_venta.valor_impuesto3 = obj.valor_impuesto3

        bd_venta.logs = [log.model_dump() for log in obj.logs]
        bd_venta.fecha_mod = obj.fecha_mod

        # Borrar e reinsertar detalle (mismo patron que update_compra)
        db.query(models_ventas.FacturaDetalle).filter(
            models_ventas.FacturaDetalle.id_trans == id_trans,
            models_ventas.FacturaDetalle.id_emp == id_emp
        ).delete()
        db.flush()

        _procesar_detalles(db, id_trans, id_emp, obj)

        # Borrar e reinsertar lineas de pago (mismo patron)
        db.query(models_ventas.FacturaMedioPago).filter(
            models_ventas.FacturaMedioPago.id_trans == id_trans,
            models_ventas.FacturaMedioPago.id_emp == id_emp
        ).delete()
        db.flush()
        _procesar_detalles_pago(db, id_trans, id_emp, obj)
        db.flush()

        db.execute(
            text("CALL public.sp_comercial_ventapos(:operacion,:parm_trans)"),
            {"operacion": "N", "parm_trans": id_trans}
        )
        db.execute(
            text("CALL public.sp_general_control_transacciones(:parm_trans)"),
            {"parm_trans": id_trans}
        )

        db.commit()
        db.refresh(bd_venta)
        return bd_venta

    except HTTPException:
        raise
    except (IntegrityError, DataError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise TransaccionValidationError(str(e.orig))


def _procesar_detalles(db: Session, id_trans: int,id_emp: str, obj: schema_ventas.ventaCreate):
        """
        Método privado para procesar e insertar detalles de venta
        Reutilizado en Creación y Edición.
        """
        for i,det in enumerate(obj.detalles, start=1):
            de_detalles = models_ventas.FacturaDetalle(     
                id_emp = id_emp,       
                id_trans = id_trans,            
                linea=i, #Numerador de linea
                #campos
                id_articulo = det.id_articulo,
                id_codbarra  = det.id_codbarra,
                referencia = det.referencia,
                precio_unit = det.precio_unit,
                cantidad  = det.cantidad,
                id_lote = det.id_lote,
                tipo_vta = "V",
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
                imp_neto=obj.imp_neto,
                imp_total = det.imp_total
            )
            db.add(de_detalles)


def _procesar_detalles_pago(db: Session, id_trans: int, id_emp: str, obj: schema_ventas.ventaCreate):
    """Inserta las lineas de pago (uno o varios medios) - sp_comercial_ventapos
    lee de esta tabla en vez de un solo id_pago fijo en la cabecera."""
    for i, det in enumerate(obj.detalles_pago, start=1):
        db.add(models_ventas.FacturaMedioPago(
            id_emp=id_emp,
            id_trans=id_trans,
            linea=i,
            id_mediopago=det.id_mediopago,
            importe=det.importe
        ))


def consultar_stock_precio_lote(db: Session, cadena: str, id_bodega: int, id_estado: int, id_lista: int):
    """Llama a ventas_obtener_stock_precio_masivo (mismo patron que
    compradirecta.consultar_stock_lote) para recalcular stock y precio de varios
    articulos en una sola consulta, usado cuando el usuario cambia bodega/estado/
    lista de precios con lineas ya cargadas en la grilla."""
    try:
        query = text("""
            SELECT idarticulo, idcodbarra, stock, precio, idimpuesto, porcentaje
            FROM public.ventas_obtener_stock_precio_masivo(:cadena, :bodega, :estado, :lista)
        """)

        result = db.execute(query, {
            "cadena": cadena,
            "bodega": id_bodega,
            "estado": id_estado,
            "lista": id_lista
        })

        return [
            {
                "idarticulo": row.idarticulo,
                "idcodbarra": row.idcodbarra,
                "stock": row.stock,
                "precio": float(row.precio),
                "idimpuesto": row.idimpuesto,
                "porcentaje": float(row.porcentaje)
            }
            for row in result
        ]

    except Exception as e:
        print(f"Error en consultar_stock_precio_lote: {str(e)}")
        return []