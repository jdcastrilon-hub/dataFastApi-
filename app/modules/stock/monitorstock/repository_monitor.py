from datetime import date
from io import BytesIO

from fastapi import HTTPException
from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import and_, desc, text
from sqlalchemy.orm import Session, contains_eager , joinedload
from app.modules.core.negocios import model_negocios
from app.modules.stock.categorias import models
from app.modules.core.sucursales import model_sucursal

def get_filtros_vista_inventario(db: Session, id_empresa: int):
        # 1. Obtenemos todos los negocios de la empresa
        negocios = db.query(model_negocios.Negocio).filter(model_negocios.Negocio.id_emp == id_empresa).all()

        # 2. Obtenemos todas las categorías de la empresa con sus subcategorías
        categorias = db.query(models.Categoria).filter(models.Categoria.id_emp == id_empresa).options(
                                    joinedload(models.Categoria.subcategorias)).all()
        
        sucursales = db.query(model_sucursal.Sucursal)\
                    .options(joinedload(model_sucursal.Sucursal.bodegas))\
                    .filter(model_sucursal.Sucursal.id_emp == id_empresa)\
                    .all()


        # 3. Mapeamos la lista de objetos Negocio al formato del DTO
        # Inyectamos la lista de categorías en cada negocio
        return {
                "idEmpresa": id_empresa,
                "listnegocio": negocios,
                "listsucursales":sucursales,
                "listCategorias":categorias
        }
        



def get_monitorinventario_data(db: Session, id_emp: int, bodega : str, negocio :str , categoria : str,subcategoria : str,page: int, size: int, articulos: list[int] | None = None):
    print ("get_monitorinventario_data")
    print (size)

    # Lista vacia equivale a "sin filtro de articulos" (la funcion de Postgres espera NULL en ese caso)
    param_articulos = articulos if articulos else None

    stats = db.execute(text("SELECT * FROM monitorstock_kpi(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_articulos )"),
                       {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria , "param_subcategoria_id" : subcategoria, "param_articulos": param_articulos}).first()

    # 3. Construyes el JSON de UI
    kpis = []

     #calculamos el total de registros
    total_records = stats.totalarticulos
    offset = page * size
    print (offset)
    # Llamada directa a la función de Postgres
    result = db.execute(
        text("SELECT * FROM monitorstock_vista1(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id , :param_limit, :param_pagina, :param_articulos)"),
         {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria , "param_subcategoria_id" : subcategoria , "param_limit":size,"param_pagina": offset, "param_articulos": param_articulos}
    ).all()
   
    # Convertir a una lista de dicts para el JSON
    items = [row._mapping for row in result]
    print (items)
    # 5. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size,
        "kpis": kpis,
        "detalles": items
    }


def get_kardex_articulo(db: Session, id_articulo: int, id_codbarra: int, fecha_inicial: date | None, fecha_final: date | None):
    result = db.execute(
        text("SELECT * FROM monitorstock_kardex(:id_articulo, :id_codbarra, :fecha_inicial, :fecha_final)"),
        {"id_articulo": id_articulo, "id_codbarra": id_codbarra, "fecha_inicial": fecha_inicial, "fecha_final": fecha_final}
    ).all()
    return [row._mapping for row in result]


def get_inventario_export_data(db: Session, id_emp: int, bodega: str, negocio: str, categoria: str, subcategoria: str, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None
    # param_incluir_limite=false: misma funcion y mismos filtros que la grilla paginada, pero trae todas las filas
    return db.execute(
        text("SELECT * FROM monitorstock_vista1(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos, false)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": 0, "param_pagina": 0, "param_articulos": param_articulos}
    ).all()


def generar_excel_inventario(filas) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventario"

    encabezados = ["Negocio", "Bodega", "Categoria", "Sub Categoria", "Articulo", "Descripcion", "Codigo de Barra", "Estado", "Unidad", "Cantidad"]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append([
            fila.negocio, fila.bodega, fila.categoria, fila.subcategoria,
            fila.cod_articulo, fila.nom_articulo, fila.cod_barra, fila.estado,
            fila.unidad, fila.cantidad
        ])

    for columna in ws.columns:
        longitud = max((len(str(celda.value)) if celda.value is not None else 0) for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = min(longitud + 2, 40)

    ws.freeze_panes = "A2"

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def get_valoracion_data(db: Session, id_emp: int, bodega: str, negocio: str, categoria: str, subcategoria: str, page: int, size: int, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None

    stats = db.execute(
        text("SELECT * FROM monitorstock_valoracion_kpi(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_articulos)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_articulos": param_articulos}
    ).first()

    total_records = stats.totalarticulos
    valor_total_inventario = stats.valortotal
    offset = page * size

    result = db.execute(
        text("SELECT * FROM monitorstock_valoracion_vista1(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": size, "param_pagina": offset, "param_articulos": param_articulos}
    ).all()

    items = [row._mapping for row in result]
    total_pages = (total_records + size - 1) // size

    return {
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size,
        "valorTotalInventario": valor_total_inventario,
        "detalles": items
    }


def get_valoracion_export_data(db: Session, id_emp: int, bodega: str, negocio: str, categoria: str, subcategoria: str, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None
    return db.execute(
        text("SELECT * FROM monitorstock_valoracion_vista1(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos, false)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": 0, "param_pagina": 0, "param_articulos": param_articulos}
    ).all()


def generar_excel_valoracion(filas) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Valoracion"

    encabezados = ["Negocio", "Bodega", "Categoria", "Sub Categoria", "Articulo", "Descripcion", "Unidad", "Cantidad", "Costo Unitario", "Valor Total"]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append([
            fila.negocio, fila.bodega, fila.categoria, fila.subcategoria,
            fila.cod_articulo, fila.nom_articulo,
            fila.unidad, fila.cantidad, float(fila.costo_unitario), float(fila.valor_total)
        ])

    for columna in ws.columns:
        longitud = max((len(str(celda.value)) if celda.value is not None else 0) for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = min(longitud + 2, 40)

    ws.freeze_panes = "A2"

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def get_stockminimo_data(db: Session, id_emp: int, bodega: str, negocio: str, categoria: str, subcategoria: str, page: int, size: int, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None

    stats = db.execute(
        text("SELECT * FROM monitorstock_stockminimo_kpi(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_articulos)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_articulos": param_articulos}
    ).first()

    total_records = stats.totalarticulos
    total_faltante = stats.totalfaltante
    offset = page * size

    result = db.execute(
        text("SELECT * FROM monitorstock_stockminimo_vista1(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": size, "param_pagina": offset, "param_articulos": param_articulos}
    ).all()

    items = [row._mapping for row in result]
    total_pages = (total_records + size - 1) // size

    return {
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size,
        "totalFaltante": total_faltante,
        "detalles": items
    }


def get_stockminimo_export_data(db: Session, id_emp: int, bodega: str, negocio: str, categoria: str, subcategoria: str, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None
    return db.execute(
        text("SELECT * FROM monitorstock_stockminimo_vista1(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos, false)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": 0, "param_pagina": 0, "param_articulos": param_articulos}
    ).all()


def generar_excel_stockminimo(filas) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Stock Minimo"

    encabezados = ["Negocio", "Categoria", "Sub Categoria", "Articulo", "Descripcion", "Unidad", "Cantidad Disponible", "Stock Minimo", "Stock Maximo", "Faltante"]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append([
            fila.negocio, fila.categoria, fila.subcategoria,
            fila.cod_articulo, fila.nom_articulo, fila.unidad,
            fila.cantidad_disponible, fila.stock_minimo, fila.stock_maximo, fila.faltante
        ])

    for columna in ws.columns:
        longitud = max((len(str(celda.value)) if celda.value is not None else 0) for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = min(longitud + 2, 40)

    ws.freeze_panes = "A2"

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


def get_vencimientos_data(db: Session, id_emp: int, bodega: str, negocio: str, categoria: str, subcategoria: str, page: int, size: int, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None

    stats = db.execute(
        text("SELECT * FROM monitorstock_vencimientos_kpi(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_articulos)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_articulos": param_articulos}
    ).first()

    total_records = stats.totallotes
    total_unidades_riesgo = stats.totalunidades
    offset = page * size

    result = db.execute(
        text("SELECT * FROM monitorstock_vencimientos_vista1(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": size, "param_pagina": offset, "param_articulos": param_articulos}
    ).all()

    items = [row._mapping for row in result]
    total_pages = (total_records + size - 1) // size

    return {
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size,
        "totalUnidadesEnRiesgo": total_unidades_riesgo,
        "detalles": items
    }


def get_vencimientos_export_data(db: Session, id_emp: int, bodega: str, negocio: str, categoria: str, subcategoria: str, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None
    return db.execute(
        text("SELECT * FROM monitorstock_vencimientos_vista1(:param_id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos, false)"),
        {"param_id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": 0, "param_pagina": 0, "param_articulos": param_articulos}
    ).all()


def generar_excel_vencimientos(filas) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Vencimientos"

    encabezados = ["Negocio", "Categoria", "Sub Categoria", "Articulo", "Descripcion", "Bodega", "Codigo Lote", "Fecha Vencimiento", "Dias para Vencer", "Cantidad"]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append([
            fila.negocio, fila.categoria, fila.subcategoria,
            fila.cod_articulo, fila.nom_articulo, fila.bodega,
            fila.codigo_lote, fila.fec_vencimiento, fila.dias_para_vencer, fila.cantidad
        ])

    for columna in ws.columns:
        longitud = max((len(str(celda.value)) if celda.value is not None else 0) for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = min(longitud + 2, 40)

    ws.freeze_panes = "A2"

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

