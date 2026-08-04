from datetime import date
from io import BytesIO

from fastapi import HTTPException
from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import and_, desc, text
from sqlalchemy.orm import Session, contains_eager , joinedload
from app.modules.compras.compradirecta import models as compras_models
from app.modules.core.negocios import model_negocios
from app.modules.stock.categorias import models
from app.modules.core.sucursales import model_sucursal

def get_filtros(db: Session, id_empresa: int):
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

def get_monitorcomprasrealizadas_data(db: Session, id_emp: int, fechainicial : date, fechafinal :date , id_sucursal: int, id_bodega : int, page: int, size: int, articulos: list[int] | None = None, proveedores: list[int] | None = None):
    param_articulos = articulos if articulos else None
    param_proveedores = proveedores if proveedores else None

    stats = db.execute(
        text("SELECT * FROM monitorcompras_kpi(:id_emp, :fechainicial, :fechafinal, :id_sucursal, :id_bodega, :proveedores, :articulos)"),
        {"id_emp": id_emp, "fechainicial": fechainicial, "fechafinal": fechafinal, "id_sucursal": id_sucursal, "id_bodega": id_bodega, "proveedores": param_proveedores, "articulos": param_articulos}
    ).first()

    # 2. Formateas en Python (esto es mucho más fácil aquí que en SQL)
    valor_formateado = f"${stats.valorcomprado / 1_000_000:.1f}M" if stats.valorcomprado >= 1_000_000 else f"${stats.valorcomprado:,.0f}"

    # 3. Construyes el JSON de UI
    kpis = [
        {
            "titulo": "Total Remitos",
            "valor": str(stats.totalremito),
            "icono": "receipt_long",
            "color": "#2196f3"
        },
        {
            "titulo": "Valor Comprado",
            "valor": valor_formateado,
            "icono": "payments",
            "color": "#673ab7"
        }
    ]

    #calculamos el total de registros
    total_records = stats.totalremito
    #Obtener los registros de la página actual
    offset = page * size

    # Llamada directa a la función de Postgres
    result = db.execute(
        text("SELECT * FROM monitorcompras_vista1(:id_emp, :fechainicial, :fechafinal, :id_sucursal, :id_bodega, :lim, :off, :proveedores, :articulos)"),
        {"id_emp": id_emp, "fechainicial": fechainicial, "fechafinal": fechafinal, "id_sucursal": id_sucursal, "id_bodega": id_bodega, "lim": size, "off": offset, "proveedores": param_proveedores, "articulos": param_articulos}
    ).all()

    # Convertir a una lista de dicts para el JSON
    items = [row._mapping for row in result]
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


def get_comprasrealizadas_export_data(db: Session, id_emp: int, fechainicial: date, fechafinal: date, id_sucursal: int, id_bodega: int, articulos: list[int] | None = None, proveedores: list[int] | None = None):
    param_articulos = articulos if articulos else None
    param_proveedores = proveedores if proveedores else None
    # param_incluir_limite=false: misma funcion y mismos filtros que la grilla paginada, pero trae todas las filas
    return db.execute(
        text("SELECT * FROM monitorcompras_vista1(:id_emp, :fechainicial, :fechafinal, :id_sucursal, :id_bodega, :lim, :off, :proveedores, :articulos, false)"),
        {"id_emp": id_emp, "fechainicial": fechainicial, "fechafinal": fechafinal, "id_sucursal": id_sucursal, "id_bodega": id_bodega, "lim": 0, "off": 0, "proveedores": param_proveedores, "articulos": param_articulos}
    ).all()


def generar_excel_comprasrealizadas(filas) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Compras Realizadas"

    encabezados = ["Fecha", "Num. OC", "Remito", "Proveedor", "Bodega", "Total"]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append([
            fila.fecha, fila.numoc, fila.remito, fila.nombreproveedor, fila.nombrebodega, float(fila.importe)
        ])

    for columna in ws.columns:
        longitud = max((len(str(celda.value)) if celda.value is not None else 0) for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = min(longitud + 2, 40)

    ws.freeze_panes = "A2"

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer

# Confirma que la compra es de la empresa activa antes de mostrar su detalle o sus
# devoluciones (monitorcompras_detalle/monitorcompras_devoluciones no filtran por
# empresa, cualquier id_trans traeria datos de cualquier compania).
def compra_pertenece_a_empresa(db: Session, id_trans: int, id_emp: int) -> bool:
    compra = db.query(compras_models.Compra.id_emp).filter(compras_models.Compra.id_trans == id_trans).first()
    return compra is not None and compra.id_emp == id_emp

def get_detalle_compra(db: Session, id_trans: int):
    result = db.execute(
        text("SELECT * FROM monitorcompras_detalle(:id_trans)"),
        {"id_trans": id_trans}
    ).all()
    return [row._mapping for row in result]


def get_devoluciones_compra(db: Session, id_compra_origen: int):
    result = db.execute(
        text("SELECT * FROM monitorcompras_devoluciones(:id_compra_origen)"),
        {"id_compra_origen": id_compra_origen}
    ).all()
    return [row._mapping for row in result]


def get_costos(db: Session, id_emp: int, bodega : str, negocio :str , categoria : str,subcategoria : str,page: int, size: int, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None

    stats = db.execute(
        text("SELECT * FROM monitorcompras_kpi_costos(:id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_articulos)"),
        {"id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria , "param_subcategoria_id" : subcategoria, "param_articulos": param_articulos}
    ).first()

    # Un solo KPI no aporta info que el paginador ya no muestre (misma convención que Inventario)
    kpis = []

     #calculamos el total de registros
    total_records = stats.totalarticulos
    offset = page * size
    # Llamada directa a la función de Postgres
    result = db.execute(
        text("SELECT * FROM monitorcompra_costo(:id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos)"),
        {"id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria , "param_subcategoria_id" : subcategoria , "param_limit":size,"param_pagina": offset, "param_articulos": param_articulos}
    ).all()

    # Convertir a una lista de dicts para el JSON
    items = [row._mapping for row in result]
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


def get_costos_export_data(db: Session, id_emp: int, bodega: str, negocio: str, categoria: str, subcategoria: str, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None
    return db.execute(
        text("SELECT * FROM monitorcompra_costo(:id_emp, :param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos, false)"),
        {"id_emp": id_emp, "param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": 0, "param_pagina": 0, "param_articulos": param_articulos}
    ).all()


def generar_excel_costos(filas) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Costos"

    encabezados = ["Negocio", "Bodega", "Categoria", "Sub Categoria", "Articulo", "Descripcion", "Costo"]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append([
            fila.negocio, fila.bodega, fila.categoria, fila.subcategoria,
            fila.cod_articulo, fila.nom_articulo, float(fila.costo)
        ])

    for columna in ws.columns:
        longitud = max((len(str(celda.value)) if celda.value is not None else 0) for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = min(longitud + 2, 40)

    ws.freeze_panes = "A2"

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
