import io
from datetime import datetime
from io import BytesIO
from typing import Optional

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill
from sqlalchemy import desc, text
from sqlalchemy.orm import Session, joinedload

from . import models
from app.core.numeradores import repository_numerador
from app.modules.stock.articulos import model_articulos
from app.modules.stock.categorias import models as models_categoria
from app.modules.stock.unidades import model_unidad
from app.modules.stock.tiposervicio import model_servicio
from app.modules.stock.bodegas import model_bodega
from app.modules.core.sucursales import model_sucursal
from app.modules.core.negocios import model_negocios

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

# Codigos de numerador (por empresa)
CODIGO_NUMERADOR_CARGASTOCK = "CARGASTOCK"
CODIGO_NUMERADOR_ARTICULO = "ARTICULO"

# Proveedor generico usado por toda carga masiva (no hay proveedor real involucrado)
COD_TIT_PROVEEDOR_GENERICO = "INVINICIAL"

COLUMNAS_OBLIGATORIAS = ["categoria", "subcategoria", "codigo", "nombre", "costo", "cantidad", "precio_venta"]
COLUMNAS_OPCIONALES = ["unidad", "tipo_servicio", "grupo_contable", "lote", "fecha_vencimiento"]

# Descripciones para la pestaña "Instrucciones" de la plantilla (columna -> (obligatoria, detalle)).
DESCRIPCION_COLUMNAS = {
    "categoria": ("Si (solo articulo nuevo)", "Debe existir en el maestro de categorias. Solo se valida si el codigo de barras es nuevo."),
    "subcategoria": ("Si (solo articulo nuevo)", "Debe existir en el maestro de subcategorias, asociada a la categoria indicada. Solo se valida si el codigo es nuevo."),
    "codigo": ("Si", "Codigo de barras del articulo. Es la clave que se usa para saber si el articulo ya existe."),
    "nombre": ("Si", "Nombre del articulo."),
    "costo": ("Si", "Costo unitario. Debe ser mayor o igual a 0."),
    "cantidad": ("Si", "Cantidad a ingresar a la bodega. Debe ser mayor a 0."),
    "precio_venta": ("Si", "Precio de venta de referencia. Por ahora es solo informativo."),
    "unidad": ("Si (solo articulo nuevo)", "Codigo de la unidad de medida; debe existir en el maestro de unidades."),
    "tipo_servicio": ("Si (solo articulo nuevo)", "Codigo del tipo de servicio; debe existir en el maestro."),
    "grupo_contable": ("Si (solo articulo nuevo)", "Grupo contable del articulo."),
    "lote": ("No", "Codigo del lote, solo si el articulo maneja lotes. Si se diligencia, 'fecha_vencimiento' es obligatoria."),
    "fecha_vencimiento": ("Condicional", "Obligatoria unicamente si se diligencio la columna 'lote'."),
}

RELLENO_OBLIGATORIA = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")


def generar_excel_plantilla() -> BytesIO:
    """Plantilla en blanco con las columnas que espera la carga masiva (solo encabezado),
    con las columnas obligatorias resaltadas en verde, mas una pestaña de instrucciones."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Plantilla"

    encabezados = COLUMNAS_OBLIGATORIAS + COLUMNAS_OPCIONALES
    ws.append(encabezados)
    for i, celda in enumerate(ws[1]):
        celda.font = Font(bold=True)
        if encabezados[i] in COLUMNAS_OBLIGATORIAS:
            celda.fill = RELLENO_OBLIGATORIA

    for columna in ws.columns:
        longitud = max(len(str(celda.value)) if celda.value is not None else 0 for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = min(max(longitud + 4, 12), 40)

    ws.freeze_panes = "A2"

    # --- Pestaña de instrucciones ---
    ws_info = wb.create_sheet("Instrucciones")
    ws_info.append(["Columna", "Obligatoria", "Detalle"])
    for celda in ws_info[1]:
        celda.font = Font(bold=True)

    for columna in encabezados:
        obligatoria, detalle = DESCRIPCION_COLUMNAS[columna]
        fila = ws_info.max_row + 1
        ws_info.append([columna, obligatoria, detalle])
        if columna in COLUMNAS_OBLIGATORIAS:
            ws_info.cell(row=fila, column=1).fill = RELLENO_OBLIGATORIA

    ws_info.column_dimensions["A"].width = 18
    ws_info.column_dimensions["B"].width = 24
    ws_info.column_dimensions["C"].width = 90
    for fila_info in ws_info.iter_rows(min_row=2):
        for celda in fila_info:
            celda.alignment = celda.alignment.copy(wrap_text=True, vertical="top")

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def _obtener_id_emp_de_bodega(db: Session, id_bodega: int):
    """Resuelve la empresa dueña de la bodega: Bodega -> Sucursal -> id_emp."""
    resultado = (
        db.query(model_sucursal.Sucursal.id_emp)
        .join(model_bodega.Bodega, model_bodega.Bodega.id_sucursal == model_sucursal.Sucursal.id)
        .filter(model_bodega.Bodega.id == id_bodega)
        .first()
    )
    return resultado[0] if resultado else None


def _obtener_o_crear_proveedor_generico(db: Session, id_emp: int) -> int:
    """El proveedor es fijo (no aplica un proveedor real en una carga masiva de inventario).
    Se crea una sola vez por empresa (m_proveedores esta particionada por id_emp)."""
    fila = db.execute(
        text("SELECT id_proveedor FROM m_proveedores WHERE id_emp=:e AND cod_tit=:c"),
        {"e": id_emp, "c": COD_TIT_PROVEEDOR_GENERICO}
    ).first()
    if fila:
        return fila[0]

    persona = db.execute(text("""
        INSERT INTO m_personas (id_tipodoc, cod_tit, nombres, apellidos, nombre_completo, id_ciudad, fecha_mod)
        VALUES (1, :c, 'Inventario Inicial', 'Sin Proveedor', 'Inventario Inicial - Sin Proveedor', 1, now())
        RETURNING id_persona
    """), {"c": COD_TIT_PROVEEDOR_GENERICO}).first()

    proveedor = db.execute(text("""
        INSERT INTO m_proveedores (id_emp, id_persona, cod_tit, razon_social, regimen, activo, observacion, fecha_mod)
        VALUES (:e, :p, :c, 'Inventario Inicial - Sin Proveedor', 'N/A', true,
                'Proveedor generico usado por la carga masiva de inventario', now())
        RETURNING id_proveedor
    """), {"e": id_emp, "p": persona[0], "c": COD_TIT_PROVEEDOR_GENERICO}).first()

    return proveedor[0]


def _leer_excel(contenido: bytes):
    libro = load_workbook(io.BytesIO(contenido), data_only=True)
    hoja = libro.active
    filas = list(hoja.iter_rows(values_only=True))
    if not filas:
        return [], []
    encabezado = [str(c).strip().lower() if c is not None else "" for c in filas[0]]
    return encabezado, filas[1:]


def _construir_indice(items, obtener_clave):
    """Indice nombre/codigo (case-insensitive) -> id. Detecta claves ambiguas (repetidas)
    para no resolver silenciosamente contra la fila equivocada."""
    indice = {}
    ambiguos = set()
    for item in items:
        clave = obtener_clave(item)
        if not clave:
            continue
        clave = clave.strip().lower()
        if clave in indice and indice[clave] != item.id:
            ambiguos.add(clave)
        indice[clave] = item.id
    return indice, ambiguos


def _texto(valor) -> str:
    if valor is None:
        return ""
    return str(valor).strip()


def _numero(valor):
    try:
        if valor is None or valor == "":
            return None
        return float(valor)
    except (TypeError, ValueError):
        return None


def procesar_carga_stock(
    db: Session,
    id_bodega: int,
    id_estado: int,
    id_negocio: int,
    fecha_movimiento,
    observacion: Optional[str],
    nombre_archivo: str,
    contenido: bytes,
    confirmar: bool,
    usuario_nombre: str,
):
    """Valida (y opcionalmente confirma/graba) una carga masiva de inventario desde Excel.
    Fase 1: valida TODAS las filas antes de tocar la base de datos; si hay algun error,
    no se graba nada y se devuelve la lista completa de errores con su numero de fila.
    Fase 2 (solo si confirmar=True y la fase 1 quedo limpia): crea articulo/codigo de
    barra/lote segun aplique, inserta el cabezal/detalle y llama el SP que impacta
    p_stock/p_costos.
    """
    encabezado, filas_excel = _leer_excel(contenido)
    if not filas_excel:
        return {"status": "error", "message": "El archivo esta vacio o no tiene filas de datos.", "errores": [], "resumen": None}

    faltantes = [c for c in COLUMNAS_OBLIGATORIAS if c not in encabezado]
    if faltantes:
        return {
            "status": "error",
            "message": "El archivo no tiene las columnas esperadas.",
            "errores": [{"fila": 1, "mensaje": f"Falta la columna '{c}'"} for c in faltantes],
            "resumen": None
        }

    idx = {nombre: pos for pos, nombre in enumerate(encabezado) if nombre}

    id_emp = _obtener_id_emp_de_bodega(db, id_bodega)
    if id_emp is None:
        return {"status": "error", "message": "No se pudo determinar la empresa de la bodega seleccionada.", "errores": [], "resumen": None}

    # --- Precarga de datos de referencia (una sola consulta cada uno, no por fila) ---
    categorias = db.query(models_categoria.Categoria).filter(models_categoria.Categoria.id_emp == id_emp).all()
    categoria_por_nombre, categorias_ambiguas = _construir_indice(categorias, lambda c: c.nom_categoria)

    ids_categoria = [c.id for c in categorias]
    subcategorias = (
        db.query(models_categoria.Subcategoria)
        .filter(models_categoria.Subcategoria.categoria_id.in_(ids_categoria))
        .all() if ids_categoria else []
    )
    subcategoria_por_clave = {}
    subcategorias_ambiguas = set()
    for s in subcategorias:
        if not s.nom_subcategoria:
            continue
        clave = (s.categoria_id, s.nom_subcategoria.strip().lower())
        if clave in subcategoria_por_clave and subcategoria_por_clave[clave] != s.id:
            subcategorias_ambiguas.add(clave)
        subcategoria_por_clave[clave] = s.id

    unidades = db.query(model_unidad.Unidad).all()
    unidad_por_codigo, _ = _construir_indice(unidades, lambda u: u.cod_unidad)

    servicios = db.query(model_servicio.TipoServicio).filter(model_servicio.TipoServicio.id_emp == id_emp).all()
    servicio_por_codigo, _ = _construir_indice(servicios, lambda s: s.cod_servicio)

    # Codigos de barra ya existentes para cualquier negocio de esta empresa
    codigosbarra_existentes = (
        db.query(model_articulos.CodigosBarra, model_articulos.Articulo)
        .join(model_articulos.Articulo, model_articulos.CodigosBarra.id_articulo == model_articulos.Articulo.id_articulo)
        .join(model_negocios.Negocio, model_articulos.Articulo.id_negocio == model_negocios.Negocio.id)
        .filter(model_negocios.Negocio.id_emp == id_emp)
        .all()
    )
    barcode_index = {
        cb.cod_barra.strip(): {"id_articulo": art.id_articulo, "id_codbarra": cb.id_codbarra, "maneja_lote": art.maneja_lote}
        for cb, art in codigosbarra_existentes if cb.cod_barra
    }

    # --- Fase 1: validar todas las filas ---
    errores = []
    filas_procesadas = []
    codigos_vistos = {}  # codigo -> lista de numeros de fila donde aparece

    for i, fila in enumerate(filas_excel, start=2):  # la fila 1 del excel es el encabezado
        if fila is None or all(c is None for c in fila):
            continue  # fila totalmente vacia, se ignora sin marcar error

        def val(nombre_col):
            pos = idx.get(nombre_col)
            return fila[pos] if pos is not None and pos < len(fila) else None

        categoria_txt = _texto(val("categoria"))
        subcategoria_txt = _texto(val("subcategoria"))
        codigo_txt = _texto(val("codigo"))
        nombre_txt = _texto(val("nombre"))
        costo_num = _numero(val("costo"))
        cantidad_num = _numero(val("cantidad"))
        precio_num = _numero(val("precio_venta"))
        unidad_txt = _texto(val("unidad"))
        servicio_txt = _texto(val("tipo_servicio"))
        grupo_contable_txt = _texto(val("grupo_contable"))
        lote_txt = _texto(val("lote"))
        fecha_venc_val = val("fecha_vencimiento")

        if not codigo_txt:
            errores.append({"fila": i, "mensaje": "El código de barras es obligatorio."})
            continue
        if not nombre_txt:
            errores.append({"fila": i, "mensaje": "El nombre del artículo es obligatorio."})
            continue
        if costo_num is None or costo_num < 0:
            errores.append({"fila": i, "mensaje": "El costo es obligatorio y debe ser mayor o igual a 0."})
            continue
        if cantidad_num is None or cantidad_num <= 0:
            errores.append({"fila": i, "mensaje": "La cantidad es obligatoria y debe ser mayor a 0."})
            continue
        if precio_num is None or precio_num < 0:
            errores.append({"fila": i, "mensaje": "El precio de venta es obligatorio y debe ser mayor o igual a 0."})
            continue

        codigos_vistos.setdefault(codigo_txt, []).append(i)

        existente = barcode_index.get(codigo_txt)
        fila_procesada = {
            "fila": i,
            "codigo": codigo_txt,
            "nombre": nombre_txt,
            "costo": costo_num,
            "cantidad": int(cantidad_num),
            "precio_venta": precio_num,
            "lote": lote_txt or None,
            "fecha_vencimiento": fecha_venc_val,
            "es_nuevo": existente is None,
        }

        if existente is not None:
            fila_procesada["id_articulo"] = existente["id_articulo"]
            fila_procesada["id_codbarra"] = existente["id_codbarra"]
            fila_procesada["maneja_lote"] = existente["maneja_lote"]
            if existente["maneja_lote"] and not lote_txt:
                errores.append({"fila": i, "mensaje": f"El artículo con código '{codigo_txt}' maneja lote; debe indicar el lote."})
                continue
        else:
            # Articulo nuevo: se requieren categoria/subcategoria/unidad/tipo_servicio/grupo_contable
            if not categoria_txt:
                errores.append({"fila": i, "mensaje": "La categoría es obligatoria para un artículo nuevo."})
                continue
            clave_cat = categoria_txt.lower()
            if clave_cat in categorias_ambiguas:
                errores.append({"fila": i, "mensaje": f"Hay más de una categoría con el nombre '{categoria_txt}'; corríjalo en el maestro de categorías."})
                continue
            id_categoria = categoria_por_nombre.get(clave_cat)
            if id_categoria is None:
                errores.append({"fila": i, "mensaje": f"La categoría '{categoria_txt}' no existe."})
                continue

            if not subcategoria_txt:
                errores.append({"fila": i, "mensaje": "La subcategoría es obligatoria para un artículo nuevo."})
                continue
            clave_sub = (id_categoria, subcategoria_txt.lower())
            if clave_sub in subcategorias_ambiguas:
                errores.append({"fila": i, "mensaje": f"Hay más de una subcategoría con el nombre '{subcategoria_txt}' en esa categoría."})
                continue
            id_subcategoria = subcategoria_por_clave.get(clave_sub)
            if id_subcategoria is None:
                errores.append({"fila": i, "mensaje": f"La subcategoría '{subcategoria_txt}' no existe en la categoría '{categoria_txt}'."})
                continue

            if not unidad_txt:
                errores.append({"fila": i, "mensaje": "La unidad es obligatoria para un artículo nuevo."})
                continue
            id_unidad = unidad_por_codigo.get(unidad_txt.lower())
            if id_unidad is None:
                errores.append({"fila": i, "mensaje": f"La unidad '{unidad_txt}' no existe."})
                continue

            if not servicio_txt:
                errores.append({"fila": i, "mensaje": "El tipo de servicio es obligatorio para un artículo nuevo."})
                continue
            id_servicio = servicio_por_codigo.get(servicio_txt.lower())
            if id_servicio is None:
                errores.append({"fila": i, "mensaje": f"El tipo de servicio '{servicio_txt}' no existe."})
                continue

            if not grupo_contable_txt:
                errores.append({"fila": i, "mensaje": "El grupo contable es obligatorio para un artículo nuevo."})
                continue

            if lote_txt and not fecha_venc_val:
                errores.append({"fila": i, "mensaje": f"El lote '{lote_txt}' requiere fecha de vencimiento."})
                continue

            fila_procesada.update({
                "categoria": categoria_txt,
                "subcategoria": subcategoria_txt,
                "id_categoria": id_categoria,
                "id_subcategoria": id_subcategoria,
                "id_unidad": id_unidad,
                "id_tiposervicio": id_servicio,
                "grupo_contable": grupo_contable_txt,
                "maneja_lote": bool(lote_txt),
            })

        filas_procesadas.append(fila_procesada)

    # Codigos de barra repetidos dentro del mismo archivo (misma linea logica, dos veces)
    for codigo, filas_num in codigos_vistos.items():
        if len(filas_num) > 1:
            errores.append({
                "fila": filas_num[0],
                "mensaje": (
                    f"El código de barras '{codigo}' aparece más de una vez en el archivo "
                    f"(filas {', '.join(map(str, filas_num))}); combínelas en una sola línea."
                )
            })

    if errores:
        return {
            "status": "error",
            "message": "El archivo tiene errores, corríjalos y vuelva a intentarlo.",
            "errores": sorted(errores, key=lambda e: e["fila"]),
            "resumen": None
        }

    articulos_nuevos = [f for f in filas_procesadas if f["es_nuevo"]]
    resumen = {
        "totalFilas": len(filas_procesadas),
        "articulosNuevos": len(articulos_nuevos),
        "articulosExistentes": len(filas_procesadas) - len(articulos_nuevos),
        "cantidadTotal": sum(f["cantidad"] for f in filas_procesadas),
        "articulosNuevosDetalle": [
            {"codigo": f["codigo"], "nombre": f["nombre"], "categoria": f["categoria"], "subcategoria": f["subcategoria"]}
            for f in articulos_nuevos
        ]
    }

    if not confirmar:
        # Solo vista previa: nada se toca en la base de datos todavia.
        return {"status": "success", "message": "Archivo validado correctamente.", "errores": [], "resumen": resumen}

    # --- Fase 2: confirmar y grabar (todo o nada) ---
    try:
        id_proveedor = _obtener_o_crear_proveedor_generico(db, id_emp)

        # IMPORTANTE: siguiente_numerador() hace su propio commit inmediato (por diseño,
        # igual que una secuencia nativa de Postgres). Si se llamara DENTRO del bucle de
        # abajo, cada llamada confirmaria de forma silenciosa todo lo que ya estuviera
        # pendiente en esta misma sesion (rompiendo el "todo o nada"). Por eso se piden
        # aqui, de una sola vez, TODOS los consecutivos que se van a necesitar, antes de
        # agregar cualquier objeto a la sesion.
        nro_docum = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_CARGASTOCK)

        codigos_articulo_nuevos = {}
        for f in filas_procesadas:
            if f["es_nuevo"]:
                valor = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_ARTICULO)
                codigos_articulo_nuevos[f["fila"]] = (
                    repository_numerador.formatear_numerador(valor) if valor else f["codigo"]
                )

        bd_cabecera = models.CargaStock(
            id_emp=id_emp,
            id_negocio=id_negocio,
            id_bodega=id_bodega,
            id_estado=id_estado,
            id_proveedor=id_proveedor,
            documento="cargastock",
            nro_docum=nro_docum,
            fecha_movimiento=fecha_movimiento,
            observacion=observacion,
            nombre_archivo=nombre_archivo,
            vista="CargaStock",
            fecha_mod=datetime.now(),
            logs=_limitar_logs([{
                "operacion": "Nuevo",
                "usuario_mod": usuario_nombre,
                "fecha_mod": str(datetime.now())
            }])
        )
        db.add(bd_cabecera)
        db.flush()

        for linea, f in enumerate(filas_procesadas, start=1):
            if f["es_nuevo"]:
                bd_articulo = model_articulos.Articulo(
                    cod_articulo=codigos_articulo_nuevos[f["fila"]],
                    nom_articulo=f["nombre"],
                    id_negocio=id_negocio,
                    id_categoria=f["id_categoria"],
                    id_subcategoria=f["id_subcategoria"],
                    id_unidad=f["id_unidad"],
                    id_tiposervicio=f["id_tiposervicio"],
                    grupo_contable=f["grupo_contable"],
                    activo_stock=True,
                    maneja_lote=f["maneja_lote"],
                    fecha_mod=datetime.now(),
                    logs=[{
                        "operacion": "Nuevo (carga masiva)",
                        "usuario_mod": usuario_nombre,
                        "fecha_mod": str(datetime.now())
                    }]
                )
                db.add(bd_articulo)
                db.flush()

                # Se inserta con SQL directo (no via el ORM): id_codbarra es parte de una
                # llave primaria compuesta, y SQLAlchemy no reconoce automaticamente esa
                # columna como autoincremental para PKs compuestas (solo lo hace para PK
                # de una sola columna) — el objeto Python se queda con id_codbarra=None
                # despues del flush aunque Postgres si le haya asignado el valor real.
                fila_codbarra = db.execute(text("""
                    INSERT INTO m_artxcodigobarra (id_articulo, cod_barra, ref_barra, estado, registro_nuevo)
                    VALUES (:art, :cod, :ref, true, true)
                    RETURNING id_codbarra
                """), {"art": bd_articulo.id_articulo, "cod": f["codigo"], "ref": f["nombre"]}).first()

                f["id_articulo"] = bd_articulo.id_articulo
                f["id_codbarra"] = fila_codbarra[0]

            id_lote = 0
            if f.get("lote"):
                fila_lote = db.execute(text("""
                    INSERT INTO m_lotes (id_articulo, codigo_lote, fec_vencimiento, fecha_mod)
                    VALUES (:art, :cod, :fec, now())
                    RETURNING id
                """), {"art": f["id_articulo"], "cod": f["lote"], "fec": f["fecha_vencimiento"]}).first()
                id_lote = fila_lote[0]

            db.add(models.DetalleCargaStock(
                id_trans=bd_cabecera.id_trans,
                id_articulo=f["id_articulo"],
                linea=linea,
                id_codbarra=f["id_codbarra"],
                id_lote=id_lote,
                id_ubicacion=0,
                costo=f["costo"],
                cantidad=f["cantidad"],
                precio_venta=f["precio_venta"]
            ))

        db.flush()

        # Impacta p_stock/p_costos (costo directo del Excel, sin promediar)
        db.execute(
            text("CALL public.sp_stock_impacto_cargastock(:operacion, :parm_trans)"),
            {"operacion": "N", "parm_trans": bd_cabecera.id_trans}
        )

        db.commit()
        db.refresh(bd_cabecera)

        return {
            "status": "success",
            "message": "Carga masiva procesada exitosamente.",
            "errores": [],
            "resumen": resumen,
            "idTrans": bd_cabecera.id_trans
        }

    except Exception:
        db.rollback()
        raise


#Paginacion
def get_cargas_paginated(db: Session, page: int, size: int, texto: str = None):
    query = db.query(models.CargaStock)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            (models.CargaStock.observacion.ilike(patron)) | (models.CargaStock.nombre_archivo.ilike(patron))
        )

    total_records = query.count()
    offset = page * size
    items = (
        query
        .options(joinedload(models.CargaStock.bodega), joinedload(models.CargaStock.estado))
        .order_by(desc(models.CargaStock.fecha_mod))
        .offset(offset)
        .limit(size)
        .all()
    )
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


# Obtener una carga por ID (para la pantalla de "ver")
def get_carga_stock(db: Session, id_trans: int):
    return (
        db.query(models.CargaStock)
        .filter(models.CargaStock.id_trans == id_trans)
        .options(joinedload(models.CargaStock.detalles).joinedload(models.DetalleCargaStock.articulo))
        .first()
    )


# Eliminar una carga (revierte su impacto en el stock/costos). No tiene edicion.
def delete_carga_stock(db: Session, id_trans: int):
    bd_cabecera = db.query(models.CargaStock).filter(models.CargaStock.id_trans == id_trans).first()
    if not bd_cabecera:
        return None

    try:
        db.execute(text("DELETE FROM p_stock WHERE id_trans = :id_trans"), {"id_trans": id_trans})
        db.execute(text("DELETE FROM p_costos WHERE id_trans = :id_trans"), {"id_trans": id_trans})
        db.query(models.DetalleCargaStock).filter(models.DetalleCargaStock.id_trans == id_trans).delete()
        db.delete(bd_cabecera)
        db.commit()
        return bd_cabecera

    except Exception:
        db.rollback()
        raise
