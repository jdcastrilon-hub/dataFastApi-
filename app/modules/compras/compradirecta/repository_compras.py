from fastapi import HTTPException
from sqlalchemy import String, cast, desc, or_, text
from sqlalchemy.exc import DataError, IntegrityError
from sqlalchemy.orm import Session , joinedload

from app.exceptions import TransaccionValidationError
from app.modules.compras.proveedores import model_proveedor
from app.core.numeradores import repository_numerador
from app.core.configuracion.validador import requerir_configurado
from . import models, schema_compras

# Codigo del numerador (por empresa) que identifica el consecutivo de nroDocum
CODIGO_NUMERADOR_COMPRA = "COMPRA"

def _siguiente_nro_docum(db: Session, id_emp: int, nro_docum_manual):
    """Asigna el nroDocum desde el numerador de la empresa (compras ya trae id_emp
    directo en la cabecera, a diferencia de ajustestock/trasladobodega que lo
    resuelven vía bodega -> sucursal). Si esa empresa tiene "requiere_consecutivo"
    en False, respeta lo enviado desde el formulario."""
    siguiente = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_COMPRA)
    return siguiente if siguiente is not None else nro_docum_manual

# Resuelve la lista general (m_listaprecio.es_general=true, activo=true) para
# impactar p_precios - mismo criterio ya usado en Carga de Stock
# (repository_cargastock.py). Solo se molesta en buscarla si de verdad hace
# falta (alguna linea trae imp_precio_vta>0); si ninguna linea tiene precio,
# no tiene sentido bloquear la compra por una lista que ni se va a usar.
def _resolver_lista_general_si_aplica(db: Session, id_emp: int, detalles: list) -> int | None:
    hay_precio_venta = any((det.imp_precio_vta or 0) > 0 for det in detalles)
    if not hay_precio_venta:
        return None

    id_lista_general = db.execute(
        text("SELECT id_lista FROM m_listaprecio WHERE id_emp = :id_emp AND es_general = true AND activo = true"),
        {"id_emp": id_emp}
    ).scalar()
    return requerir_configurado(
        id_lista_general,
        "La empresa no tiene una lista de precios general activa; configúrela en "
        "Comercial > Listas de Precio antes de registrar precios de venta en la compra."
    )

#Paginacion (filtrada por empresa)
def get_compras_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(models.Compra).filter(models.Compra.id_emp == id_emp)

    # Filtro de busqueda por documento, remito o nombre del proveedor (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query\
            .join(models.Compra.proveedor)\
            .filter(
                or_(
                    models.Compra.remito.ilike(patron),
                    cast(models.Compra.nro_docum, String).ilike(patron),
                    model_proveedor.Proveedor.razon_social.ilike(patron)
                )
            )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query\
        .options(
            joinedload(models.Compra.proveedor),
            joinedload(models.Compra.bodega))\
        .order_by(desc(models.Compra.fecha_mod))\
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
                    joinedload(models.Compra.nuevoLote),
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
def create_compra(db: Session, obj: schema_compras.CompraCreate) :
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        #Capturamos numerador para la compra directa
        nro_docum = _siguiente_nro_docum(db, obj.id_emp, obj.nro_docum)
        # 1. Crear el objeto principal
        bd_compra = models.Compra(
            id_emp=obj.id_emp,
            id_sucursal=obj.id_sucursal,
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
            usuario_mod = logs_dict[-1].get('usuario_mod') if logs_dict else None
            id_lista_general = _resolver_lista_general_si_aplica(db, obj.id_emp, obj.detalles)
            db.execute(
                text("CALL public.sp_compradirecta(:operacion,:parm_trans,:usuario,:id_lista)"),
                {"operacion": "N", "parm_trans": bd_compra.id_trans, "usuario": usuario_mod, "id_lista": id_lista_general}
            )

            #Control de transaccion
            db.execute(
                text("CALL public.sp_general_control_transacciones(:parm_trans)"), 
                {"parm_trans": bd_compra.id_trans}
            )     
        
        db.commit()
        db.refresh(bd_compra)
        return bd_compra

    except HTTPException:
        # Ej. "falta configurar la lista de precios general" (requerir_configurado
        # en _resolver_lista_general_si_aplica): se deja pasar tal cual, no se
        # reenvuelve como TransaccionValidationError (que asume un e.orig de SP/BD).
        db.rollback()
        raise
    except (IntegrityError, DataError):
        # No se envuelve: se deja que el manejador global responda con el mensaje
        # amigable específico (ej. remito duplicado para el mismo proveedor/empresa,
        # restricción UNIQUE (id_emp, id_proveedor, remito) ya existente en la BD).
        db.rollback()
        raise
    except Exception as e:
        # Lo que llega aquí son errores de negocio lanzados por los SPs (ej.
        # sp_general_control_stock haciendo RAISE EXCEPTION 'ERR_VAL: ...'), no
        # violaciones de integridad — esos ya se filtraron arriba.
        db.rollback() # ¡Fundamental! Deshace todo si algo falla
        raise TransaccionValidationError(str(e.orig))

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
        bd_compra.id_sucursal = obj.id_sucursal
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
        db.query(models.DetalleCompraNuevoLote).filter(models.DetalleCompraNuevoLote.id_trans == id_trans).delete()
        db.flush() # Ejecuta los deletes pero mantiene la transacción abierta
       
        # Insertar Detalles
        _procesar_detalles_y_codigos(db, bd_compra.id_trans, obj)
        db.flush() # Envio a base de datos

        # 5. Lógica del Store Procedure para Edición
        if obj.status == 'F':
            # Llamamos al SP con operación 'E' (Edit) o la que maneje tu lógica de Matrix
            usuario_mod = bd_compra.logs[-1].get('usuario_mod') if bd_compra.logs else None
            id_lista_general = _resolver_lista_general_si_aplica(db, bd_compra.id_emp, obj.detalles)
            db.execute(
                text("CALL public.sp_compradirecta(:operacion, :parm_trans, :usuario, :id_lista)"),
                {"operacion": "N", "parm_trans": id_trans, "usuario": usuario_mod, "id_lista": id_lista_general}
            )
        
        db.commit()
        db.refresh(bd_compra)
        return bd_compra

    except HTTPException:
        # "Compra no encontrada" (404) lanzada arriba: se deja pasar tal cual, no se
        # reenvuelve como un 400 generico.
        raise
    except (IntegrityError, DataError):
        # Mismo motivo que en create_compra: se deja que el manejador global de
        # errores de integridad responda con el mensaje amigable especifico.
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al editar la compra: {str(e)}")

# Eliminar una compra. Si estaba finalizada ('F'), su impacto en stock/costos ya fue
# materializado por sp_compradirecta (p_stock/p_costos) y ese SP no tiene modo "reversa",
# asi que hay que revertirlo a mano antes de borrar (mismo patron que ajustestock/trasladobodega).
# Los codigos de barra que el SP ya haya materializado en m_artxcodigobarra NO se tocan:
# quedan como parte del catalogo, la compra que los origino ya no es lo que los sostiene.
def delete_compra(db: Session, id_trans: int):
    bd_compra = db.query(models.Compra).filter(models.Compra.id_trans == id_trans).first()
    if not bd_compra:
        return None

    try:
        db.execute(text("DELETE FROM public.p_stock WHERE id_trans=:parm_trans"), {"parm_trans": id_trans})
        db.execute(text("DELETE FROM public.p_costos WHERE id_trans=:parm_trans"), {"parm_trans": id_trans})
        # p_precios no tiene trigger de DELETE (a diferencia de p_costos): borrar
        # estas filas limpia el historial de esta transaccion, pero NO revierte
        # el precio actual del articulo en s_precioxarticulo - decision explicita,
        # ver migracion 9f2c6a1e4d78 (para cuando se borra la compra ya pudo haber
        # ventas reales con el precio nuevo).
        db.execute(text("DELETE FROM public.p_precios WHERE id_trans=:parm_trans"), {"parm_trans": id_trans})

        db.delete(bd_compra)  # cascade borra detalles (td_compras) y nuevoCodigoBarra (td_comprasnewcodbarra)
        db.commit()
        return bd_compra
    except Exception:
        db.rollback()
        raise

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
                imp_precio_vta = det.imp_precio_vta,
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

        # 4. Staging de lotes nuevos: aun no existen en m_lotes, el SP los crea
        # como parte del mismo commit (ver sp_compradirecta).
        for i, lote in enumerate(obj.nuevos_lotes, start=1):
            db.add(models.DetalleCompraNuevoLote(
                id_trans=id_trans,
                id_articulo=lote.id_articulo,
                id_lote=lote.id_lote,
                linea=i,
                codigo_lote=lote.codigo_lote,
                fec_vencimiento=lote.fec_vencimiento
            ))