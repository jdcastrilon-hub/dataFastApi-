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
from app.modules.impuestos.impuesto import modal_impuesto
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

COLUMNAS_OBLIGATORIAS = ["referencia_articulo", "categoria", "subcategoria", "codigo", "nombre", "costo", "cantidad", "precio_venta"]
COLUMNAS_OPCIONALES = ["unidad", "tipo_servicio", "grupo_contable", "impuesto", "lote", "fecha_vencimiento"]

# Columnas resaltadas en verde en la plantilla (mas amplio que COLUMNAS_OBLIGATORIAS: incluye
# columnas que solo son obligatorias para articulos nuevos, pero que igual conviene destacar).
COLUMNAS_RESALTADAS_VERDE = COLUMNAS_OBLIGATORIAS + ["unidad", "impuesto"]

# Descripciones para la pestaña "Instrucciones" de la plantilla (columna -> (obligatoria, detalle)).
DESCRIPCION_COLUMNAS = {
    "referencia_articulo": ("Si", "Numero o texto libre que usted asigna. Use el MISMO valor en todas las filas que sean el mismo articulo con distintos codigos de barra (ej: 1, 1, 2, 3...); cada valor distinto es un articulo diferente."),
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
    "impuesto": ("Si (solo articulo nuevo)", "Nombre exacto de la tasa segun el maestro de impuestos (ej: 'IVA 19%', 'IVA 0%'). Debe existir previamente."),
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
        if encabezados[i] in COLUMNAS_RESALTADAS_VERDE:
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
        if columna in COLUMNAS_RESALTADAS_VERDE:
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
    Se crea un m_proveedores por empresa (particionada por id_emp, cod_tit - ver
    m_proveedores_uniq). PERO m_personas es una tabla compartida entre empresas (no tiene
    id_emp) y su cod_tit es UNIQUE global (m_personas_uniq): si otra empresa ya hizo una
    carga masiva antes, la persona 'INVINICIAL' ya existe y hay que reutilizarla, no
    volver a insertarla (eso violaria el unique global y tumbaba toda la transaccion,
    incluso para empresas que nunca habian usado este proveedor)."""
    fila = db.execute(
        text("SELECT id_proveedor FROM m_proveedores WHERE id_emp=:e AND cod_tit=:c"),
        {"e": id_emp, "c": COD_TIT_PROVEEDOR_GENERICO}
    ).first()
    if fila:
        return fila[0]

    persona_existente = db.execute(
        text("SELECT id_persona FROM m_personas WHERE cod_tit=:c"),
        {"c": COD_TIT_PROVEEDOR_GENERICO}
    ).first()

    if persona_existente:
        id_persona = persona_existente[0]
    else:
        persona = db.execute(text("""
            INSERT INTO m_personas (id_tipodoc, cod_tit, nombres, apellidos, nombre_completo, id_ciudad, fecha_mod)
            VALUES (1, :c, 'Inventario Inicial', 'Sin Proveedor', 'Inventario Inicial - Sin Proveedor', 1, now())
            RETURNING id_persona
        """), {"c": COD_TIT_PROVEEDOR_GENERICO}).first()
        id_persona = persona[0]

    proveedor = db.execute(text("""
        INSERT INTO m_proveedores (id_emp, id_persona, cod_tit, razon_social, regimen, activo, observacion, fecha_mod)
        VALUES (:e, :p, :c, 'Inventario Inicial - Sin Proveedor', 'N/A', true,
                'Proveedor generico usado por la carga masiva de inventario', now())
        RETURNING id_proveedor
    """), {"e": id_emp, "p": id_persona, "c": COD_TIT_PROVEEDOR_GENERICO}).first()

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
    Las filas se agrupan por "referencia_articulo": varias filas con la misma referencia
    son el mismo articulo fisico con distintos codigos de barra (ver Fase 1b).
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

    # El precio_venta de cada fila se impacta en p_precios contra la lista general
    # activa de la empresa (ver m_listaprecio.es_general); sin ella no hay donde
    # registrar el precio, asi que se bloquea la carga completa.
    id_lista_general = db.execute(
        text("SELECT id_lista FROM m_listaprecio WHERE id_emp = :id_emp AND es_general = true AND activo = true"),
        {"id_emp": id_emp}
    ).scalar()
    if id_lista_general is None:
        return {
            "status": "error",
            "message": "La empresa no tiene una lista de precios general activa; configúrela antes de hacer la carga masiva.",
            "errores": [],
            "resumen": None
        }

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

    unidades = db.query(model_unidad.Unidad).filter(model_unidad.Unidad.id_emp == id_emp).all()
    unidad_por_codigo, _ = _construir_indice(unidades, lambda u: u.cod_unidad)

    servicios = db.query(model_servicio.TipoServicio).filter(model_servicio.TipoServicio.id_emp == id_emp).all()
    servicio_por_codigo, _ = _construir_indice(servicios, lambda s: s.cod_servicio)

    impuestos = db.query(modal_impuesto.Impuesto).filter(modal_impuesto.Impuesto.id_emp == id_emp).all()
    impuesto_por_nombre, impuestos_ambiguos = _construir_indice(impuestos, lambda i: i.nombre_tasa)

    # Codigos de barra ya existentes para cualquier negocio de esta empresa
    codigosbarra_existentes = (
        db.query(model_articulos.CodigosBarra, model_articulos.Articulo)
        .join(model_articulos.Articulo, model_articulos.CodigosBarra.id_articulo == model_articulos.Articulo.id_articulo)
        .join(model_negocios.Negocio, model_articulos.Articulo.id_negocio == model_negocios.Negocio.id)
        .filter(model_negocios.Negocio.id_emp == id_emp)
        .all()
    )
    # No hay UNIQUE en cod_barra (a proposito: dos articulos distintos pueden legitimamente
    # compartir un mismo codigo, ej. llego asi en una compra). Se detecta esa ambiguedad para
    # no adivinar a cual articulo pertenece (ver barcodes_ambiguos mas abajo).
    barcode_index = {}
    barcode_articulos = {}
    for cb, art in codigosbarra_existentes:
        if not cb.cod_barra:
            continue
        codigo = cb.cod_barra.strip()
        barcode_articulos.setdefault(codigo, set()).add(art.id_articulo)
        barcode_index[codigo] = {"id_articulo": art.id_articulo, "id_codbarra": cb.id_codbarra, "maneja_lote": art.maneja_lote}
    barcodes_ambiguos = {codigo: ids for codigo, ids in barcode_articulos.items() if len(ids) > 1}

    # --- Fase 1a: parseo y validaciones por fila (columnas independientes de la agrupacion) ---
    errores = []
    filas_procesadas = []
    codigos_vistos = {}  # codigo -> lista de numeros de fila donde aparece

    for i, fila in enumerate(filas_excel, start=2):  # la fila 1 del excel es el encabezado
        if fila is None or all(c is None for c in fila):
            continue  # fila totalmente vacia, se ignora sin marcar error

        def val(nombre_col):
            pos = idx.get(nombre_col)
            return fila[pos] if pos is not None and pos < len(fila) else None

        referencia_txt = _texto(val("referencia_articulo"))
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
        impuesto_txt = _texto(val("impuesto"))
        lote_txt = _texto(val("lote"))
        fecha_venc_val = val("fecha_vencimiento")

        if not referencia_txt:
            errores.append({"fila": i, "mensaje": "La referencia del artículo (referencia_articulo) es obligatoria."})
            continue
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
        if lote_txt and not fecha_venc_val:
            errores.append({"fila": i, "mensaje": f"El lote '{lote_txt}' requiere fecha de vencimiento."})
            continue

        if codigo_txt in barcodes_ambiguos:
            ids_txt = ", ".join(str(x) for x in sorted(barcodes_ambiguos[codigo_txt]))
            errores.append({
                "fila": i,
                "mensaje": f"El código de barras '{codigo_txt}' está asociado a más de un artículo (ID {ids_txt}); no se puede determinar a cuál pertenece esta fila. Corríjalo en el módulo de Artículos antes de continuar."
            })
            continue

        codigos_vistos.setdefault(codigo_txt, []).append(i)

        existente = barcode_index.get(codigo_txt)
        fila_procesada = {
            "fila": i,
            "referencia": referencia_txt,
            "codigo": codigo_txt,
            "nombre": nombre_txt,
            "costo": costo_num,
            "cantidad": int(cantidad_num),
            "precio_venta": precio_num,
            "lote": lote_txt or None,
            "fecha_vencimiento": fecha_venc_val,
            "existente_directo": existente is not None,
            "id_articulo": existente["id_articulo"] if existente else None,
            "id_codbarra": existente["id_codbarra"] if existente else None,
            # Campos crudos de articulo: solo se usan/validan si esta fila termina siendo
            # la representante de un grupo (misma referencia_articulo) enteramente nuevo.
            "categoria_txt": categoria_txt,
            "subcategoria_txt": subcategoria_txt,
            "unidad_txt": unidad_txt,
            "servicio_txt": servicio_txt,
            "grupo_contable_txt": grupo_contable_txt,
            "impuesto_txt": impuesto_txt,
        }

        if existente is not None:
            fila_procesada["maneja_lote"] = existente["maneja_lote"]
            if existente["maneja_lote"] and not lote_txt:
                errores.append({"fila": i, "mensaje": f"El artículo con código '{codigo_txt}' maneja lote; debe indicar el lote."})
                continue

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

    # --- Fase 1b: agrupar por referencia_articulo y resolver cada grupo ---
    # Filas con la misma referencia son el mismo articulo fisico (posiblemente con varios
    # codigos de barra). Si alguna fila del grupo coincide con un articulo ya existente,
    # todo el grupo se cuelga de ese articulo (las demas filas solo aportan un codigo de
    # barra mas). Si ninguna coincide, la primera fila del grupo (orden de aparicion en el
    # archivo) define los datos del articulo nuevo a crear; las demas filas del grupo no
    # necesitan repetir esos datos, solo su propio codigo/costo/cantidad/precio_venta.
    grupos = {}
    for f in filas_procesadas:
        grupos.setdefault(f["referencia"], []).append(f)

    for referencia, filas_grupo in grupos.items():
        ids_existentes_grupo = {f["id_articulo"] for f in filas_grupo if f["existente_directo"]}

        if len(ids_existentes_grupo) > 1:
            errores.append({
                "fila": filas_grupo[0]["fila"],
                "mensaje": f"La referencia '{referencia}' coincide con más de un artículo ya existente distinto; revise los códigos de barra de esas filas."
            })
            continue

        if ids_existentes_grupo:
            # El grupo completo se cuelga del articulo ya existente.
            id_articulo_grupo = next(iter(ids_existentes_grupo))
            maneja_lote_grupo = next(f["maneja_lote"] for f in filas_grupo if f["existente_directo"])
            for f in filas_grupo:
                if not f["existente_directo"]:
                    f["id_articulo"] = id_articulo_grupo
                    f["maneja_lote"] = maneja_lote_grupo
                    if maneja_lote_grupo and not f["lote"]:
                        errores.append({"fila": f["fila"], "mensaje": f"El artículo de la referencia '{referencia}' ya existe y maneja lote; debe indicar el lote."})
            continue

        # Grupo enteramente nuevo: la primera fila (por orden de aparicion) define el articulo.
        representante = filas_grupo[0]

        if not representante["categoria_txt"]:
            errores.append({"fila": representante["fila"], "mensaje": "La categoría es obligatoria para un artículo nuevo."})
            continue
        clave_cat = representante["categoria_txt"].lower()
        if clave_cat in categorias_ambiguas:
            errores.append({"fila": representante["fila"], "mensaje": f"Hay más de una categoría con el nombre '{representante['categoria_txt']}'; corríjalo en el maestro de categorías."})
            continue
        id_categoria = categoria_por_nombre.get(clave_cat)
        if id_categoria is None:
            errores.append({"fila": representante["fila"], "mensaje": f"La categoría '{representante['categoria_txt']}' no existe."})
            continue

        if not representante["subcategoria_txt"]:
            errores.append({"fila": representante["fila"], "mensaje": "La subcategoría es obligatoria para un artículo nuevo."})
            continue
        clave_sub = (id_categoria, representante["subcategoria_txt"].lower())
        if clave_sub in subcategorias_ambiguas:
            errores.append({"fila": representante["fila"], "mensaje": f"Hay más de una subcategoría con el nombre '{representante['subcategoria_txt']}' en esa categoría."})
            continue
        id_subcategoria = subcategoria_por_clave.get(clave_sub)
        if id_subcategoria is None:
            errores.append({"fila": representante["fila"], "mensaje": f"La subcategoría '{representante['subcategoria_txt']}' no existe en la categoría '{representante['categoria_txt']}'."})
            continue

        if not representante["unidad_txt"]:
            errores.append({"fila": representante["fila"], "mensaje": "La unidad es obligatoria para un artículo nuevo."})
            continue
        id_unidad = unidad_por_codigo.get(representante["unidad_txt"].lower())
        if id_unidad is None:
            errores.append({"fila": representante["fila"], "mensaje": f"La unidad '{representante['unidad_txt']}' no existe."})
            continue

        if not representante["servicio_txt"]:
            errores.append({"fila": representante["fila"], "mensaje": "El tipo de servicio es obligatorio para un artículo nuevo."})
            continue
        id_servicio = servicio_por_codigo.get(representante["servicio_txt"].lower())
        if id_servicio is None:
            errores.append({"fila": representante["fila"], "mensaje": f"El tipo de servicio '{representante['servicio_txt']}' no existe."})
            continue

        if not representante["grupo_contable_txt"]:
            errores.append({"fila": representante["fila"], "mensaje": "El grupo contable es obligatorio para un artículo nuevo."})
            continue

        if not representante["impuesto_txt"]:
            errores.append({"fila": representante["fila"], "mensaje": "El impuesto (IVA) es obligatorio para un artículo nuevo."})
            continue
        clave_imp = representante["impuesto_txt"].lower()
        if clave_imp in impuestos_ambiguos:
            errores.append({"fila": representante["fila"], "mensaje": f"Hay más de un impuesto con el nombre '{representante['impuesto_txt']}'; corríjalo en el maestro de impuestos."})
            continue
        id_impuesto = impuesto_por_nombre.get(clave_imp)
        if id_impuesto is None:
            errores.append({"fila": representante["fila"], "mensaje": f"El impuesto '{representante['impuesto_txt']}' no existe."})
            continue

        maneja_lote_grupo = any(bool(f["lote"]) for f in filas_grupo)
        datos_articulo_nuevo = {
            "categoria": representante["categoria_txt"],
            "subcategoria": representante["subcategoria_txt"],
            "id_categoria": id_categoria,
            "id_subcategoria": id_subcategoria,
            "id_unidad": id_unidad,
            "id_tiposervicio": id_servicio,
            "grupo_contable": representante["grupo_contable_txt"],
            "id_impuesto": id_impuesto,
            "nombre": representante["nombre"],
            "codigo": representante["codigo"],
        }
        for f in filas_grupo:
            f["maneja_lote"] = maneja_lote_grupo
            f["grupo_nuevo_datos"] = datos_articulo_nuevo

    # Grupos que van a crear un articulo nuevo (aun no tienen id_articulo asignado).
    grupos_nuevos = [ref for ref, filas_grupo in grupos.items() if filas_grupo[0]["id_articulo"] is None]

    # Nombres duplicados entre articulos nuevos DISTINTOS (referencia_articulo diferente):
    # es la senal de que dos filas son en realidad el mismo articulo pero el usuario no
    # las vinculo con la misma referencia. No se adivina: se marca como error para que
    # el usuario decida (misma referencia si es el mismo articulo, o corregir el nombre
    # si en verdad son productos distintos).
    nombres_nuevos = {}
    for referencia in grupos_nuevos:
        representante = grupos[referencia][0]
        clave_nombre = representante["nombre"].strip().lower()
        nombres_nuevos.setdefault(clave_nombre, []).append(representante)

    for clave_nombre, representantes in nombres_nuevos.items():
        if len(representantes) > 1:
            filas_num = sorted(r["fila"] for r in representantes)
            errores.append({
                "fila": filas_num[0],
                "mensaje": (
                    f"El nombre '{representantes[0]['nombre']}' se repite en más de un artículo nuevo "
                    f"(filas {', '.join(map(str, filas_num))}); si es el mismo artículo, use la misma "
                    f"referencia_articulo en esas filas, o corrija el nombre si son artículos distintos."
                )
            })

    if errores:
        return {
            "status": "error",
            "message": "El archivo tiene errores, corríjalos y vuelva a intentarlo.",
            "errores": sorted(errores, key=lambda e: e["fila"]),
            "resumen": None
        }

    # Resumen a nivel de articulo/grupo (no de fila): varias filas pueden ser el mismo articulo.
    resumen = {
        "totalFilas": len(filas_procesadas),
        "articulosNuevos": len(grupos_nuevos),
        "articulosExistentes": len({f["id_articulo"] for f in filas_procesadas if f["id_articulo"] is not None}),
        "cantidadTotal": sum(f["cantidad"] for f in filas_procesadas),
        "articulosNuevosDetalle": [
            {
                "codigo": grupos[ref][0]["grupo_nuevo_datos"]["codigo"],
                "nombre": grupos[ref][0]["grupo_nuevo_datos"]["nombre"],
                "categoria": grupos[ref][0]["grupo_nuevo_datos"]["categoria"],
                "subcategoria": grupos[ref][0]["grupo_nuevo_datos"]["subcategoria"],
            }
            for ref in grupos_nuevos
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

        # Un consecutivo de cod_articulo POR GRUPO nuevo (no por fila): varias filas del
        # mismo grupo (misma referencia_articulo) terminan siendo un solo articulo.
        codigos_articulo_nuevos = {}
        for referencia in grupos_nuevos:
            valor = repository_numerador.siguiente_numerador(db, id_emp, CODIGO_NUMERADOR_ARTICULO)
            codigos_articulo_nuevos[referencia] = (
                repository_numerador.formatear_numerador(valor) if valor else grupos[referencia][0]["codigo"]
            )

        # Precio vigente hoy en la lista general para los articulos que YA existian
        # (los nuevos, por definicion, no tienen precio_anterior). Se precarga una
        # sola vez, no por fila.
        ids_articulo_existentes = {f["id_articulo"] for f in filas_procesadas if f["id_articulo"] is not None}
        precios_actuales = {}
        if ids_articulo_existentes:
            filas_precio = db.execute(
                text("SELECT id_articulo, precio_venta FROM s_precioxarticulo WHERE id_lista = :lista AND id_articulo = ANY(:ids)"),
                {"lista": id_lista_general, "ids": list(ids_articulo_existentes)}
            ).all()
            precios_actuales = {r.id_articulo: r.precio_venta for r in filas_precio}

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

        articulos_creados_por_grupo = {}  # referencia -> id_articulo recien creado

        for linea, f in enumerate(filas_procesadas, start=1):
            if f["id_articulo"] is None:
                referencia = f["referencia"]
                if referencia not in articulos_creados_por_grupo:
                    # Primera fila de este grupo que se procesa: crea el articulo una sola
                    # vez, con los datos ya resueltos en Fase 1b (de la fila representante).
                    datos = f["grupo_nuevo_datos"]
                    bd_articulo = model_articulos.Articulo(
                        cod_articulo=codigos_articulo_nuevos[referencia],
                        nom_articulo=datos["nombre"],
                        id_emp=id_emp,
                        id_negocio=id_negocio,
                        id_categoria=datos["id_categoria"],
                        id_subcategoria=datos["id_subcategoria"],
                        id_unidad=datos["id_unidad"],
                        id_tiposervicio=datos["id_tiposervicio"],
                        grupo_contable=datos["grupo_contable"],
                        id_impuesto=datos["id_impuesto"],
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
                    articulos_creados_por_grupo[referencia] = bd_articulo.id_articulo
                f["id_articulo"] = articulos_creados_por_grupo[referencia]

            if f["id_codbarra"] is None:
                # Codigo de barra nuevo: ya sea de un articulo recien creado o uno mas que
                # se agrega a un articulo existente (misma referencia que otra fila con
                # codigo ya existente). Se inserta con SQL directo (no via el ORM):
                # id_codbarra es parte de una llave primaria compuesta, y SQLAlchemy no
                # reconoce automaticamente esa columna como autoincremental para PKs
                # compuestas (solo lo hace para PK de una sola columna) — el objeto Python
                # se queda con id_codbarra=None despues del flush aunque Postgres si le
                # haya asignado el valor real.
                fila_codbarra = db.execute(text("""
                    INSERT INTO m_artxcodigobarra (id_articulo, cod_barra, ref_barra, estado, registro_nuevo)
                    VALUES (:art, :cod, :ref, true, true)
                    RETURNING id_codbarra
                """), {"art": f["id_articulo"], "cod": f["codigo"], "ref": f["nombre"]}).first()
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

            # Impacta p_precios contra la lista general: el trigger ins_p_precios
            # actualiza el snapshot s_precioxarticulo, y ins_p_precios_reglas
            # propaga automaticamente a las listas de cliente con regla de categoria
            # activa (ver alembic 9c8225580f88). No hay modelo ORM para p_precios
            # (mismo criterio que p_stock/p_costos: ledger sin FKs, insert directo).
            db.execute(text("""
                INSERT INTO p_precios (id_trans, linea, id_emp, id_lista, id_articulo,
                    precio_anterior, precio_nuevo, origen, usuario_mod, fecha_mod)
                VALUES (:id_trans, :linea, :id_emp, :id_lista, :id_articulo,
                    :precio_anterior, :precio_nuevo, 'CARGA_ITEMS', :usuario_mod, :fecha_mod)
            """), {
                "id_trans": bd_cabecera.id_trans,
                "linea": linea,
                "id_emp": id_emp,
                "id_lista": id_lista_general,
                "id_articulo": f["id_articulo"],
                "precio_anterior": precios_actuales.get(f["id_articulo"]),
                "precio_nuevo": f["precio_venta"],
                "usuario_mod": usuario_nombre,
                "fecha_mod": datetime.now()
            })

        db.flush()

        # Impacta p_stock/p_costos (costo directo del Excel, sin promediar)
        db.execute(
            text("CALL public.sp_stock_impacto_cargastock(:operacion, :parm_trans, :usuario)"),
            {"operacion": "N", "parm_trans": bd_cabecera.id_trans, "usuario": usuario_nombre}
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

# No hay funcion de eliminar a proposito (ver nota en controller_cargastock.py): este
# modulo es solo para la carga inicial de inventario, no una operacion recurrente.
