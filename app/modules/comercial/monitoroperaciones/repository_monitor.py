from datetime import date
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload
from app.modules.core.sucursales import model_sucursal
from app.modules.core.negocios import model_negocios
from app.modules.stock.categorias import models as categoria_models
from app.modules.comercial.listaprecio import model_listaprecio


def get_filtros(db: Session, id_empresa: int):
    sucursales = db.query(model_sucursal.Sucursal)\
        .options(joinedload(model_sucursal.Sucursal.caja))\
        .filter(model_sucursal.Sucursal.id_emp == id_empresa)\
        .all()

    negocios = db.query(model_negocios.Negocio).filter(model_negocios.Negocio.id_emp == id_empresa).all()

    categorias = db.query(categoria_models.Categoria)\
        .filter(categoria_models.Categoria.id_emp == id_empresa)\
        .options(joinedload(categoria_models.Categoria.subcategorias))\
        .all()

    # Solo listas base (nunca de cliente) - ver ListaPrecioSchema.
    listas_precio = db.query(model_listaprecio.MListaPrecio)\
        .filter(
            model_listaprecio.MListaPrecio.id_emp == id_empresa,
            model_listaprecio.MListaPrecio.id_cliente.is_(None),
            model_listaprecio.MListaPrecio.activo.is_(True)
        )\
        .order_by(model_listaprecio.MListaPrecio.nombre)\
        .all()

    return {
        "idEmpresa": id_empresa,
        "listsucursales": sucursales,
        "listnegocio": negocios,
        "listCategorias": categorias,
        "listListaPrecio": listas_precio
    }


def get_ventasrealizadas_data(
    db: Session, id_emp: int, fechainicial: date, fechafinal: date,
    id_sucursal: int, id_caja: int, page: int, size: int,
    tipos_documento: list[str] | None = None,
    solo_con_descuento: bool = False,
    clientes: list[int] | None = None,
    articulos: list[int] | None = None
):
    param_tipos_documento = tipos_documento if tipos_documento else None
    param_clientes = clientes if clientes else None
    param_articulos = articulos if articulos else None

    stats = db.execute(
        text("SELECT * FROM monitoroperaciones_ventas_kpi(:id_emp, :fechainicial, :fechafinal, :id_sucursal, :id_caja, :tipos_documento, :solo_con_descuento, :clientes, :articulos)"),
        {"id_emp": id_emp, "fechainicial": fechainicial, "fechafinal": fechafinal, "id_sucursal": id_sucursal, "id_caja": id_caja,
         "tipos_documento": param_tipos_documento, "solo_con_descuento": solo_con_descuento, "clientes": param_clientes, "articulos": param_articulos}
    ).first()

    valor_formateado = f"${stats.valorvendido / 1_000_000:.1f}M" if stats.valorvendido >= 1_000_000 else f"${stats.valorvendido:,.0f}"

    kpis = [
        {
            "titulo": "Total Ventas",
            "valor": str(stats.totalventas),
            "icono": "receipt_long",
            "color": "#2196f3"
        },
        {
            "titulo": "Valor Vendido",
            "valor": valor_formateado,
            "icono": "payments",
            "color": "#43a047"
        }
    ]

    total_records = stats.totalventas
    offset = page * size

    result = db.execute(
        text("SELECT * FROM monitoroperaciones_ventas_vista1(:id_emp, :fechainicial, :fechafinal, :id_sucursal, :id_caja, :lim, :off, :tipos_documento, :solo_con_descuento, :clientes, :articulos)"),
        {"id_emp": id_emp, "fechainicial": fechainicial, "fechafinal": fechafinal, "id_sucursal": id_sucursal, "id_caja": id_caja, "lim": size, "off": offset,
         "tipos_documento": param_tipos_documento, "solo_con_descuento": solo_con_descuento, "clientes": param_clientes, "articulos": param_articulos}
    ).all()

    items = [row._mapping for row in result]
    total_pages = (total_records + size - 1) // size

    return {
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size,
        "kpis": kpis,
        "detalles": items
    }


def get_precios(db: Session, id_emp: int, lista: int, negocio: int, categoria: int, subcategoria: int, page: int, size: int, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None

    stats = db.execute(
        text("SELECT * FROM monitorventas_kpi_precio(:id_emp, :param_lista_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_articulos)"),
        {"id_emp": id_emp, "param_lista_id": lista, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_articulos": param_articulos}
    ).first()

    # Un solo KPI no aporta info que el paginador ya no muestre (misma convencion que costos)
    kpis = []

    total_records = stats.totalarticulos
    offset = page * size

    result = db.execute(
        text("SELECT * FROM monitorventas_precio(:id_emp, :param_lista_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos)"),
        {"id_emp": id_emp, "param_lista_id": lista, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": size, "param_pagina": offset, "param_articulos": param_articulos}
    ).all()

    items = [row._mapping for row in result]
    total_pages = (total_records + size - 1) // size

    return {
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size,
        "kpis": kpis,
        "detalles": items
    }


def get_precios_export_data(db: Session, id_emp: int, lista: int, negocio: int, categoria: int, subcategoria: int, articulos: list[int] | None = None):
    param_articulos = articulos if articulos else None
    return db.execute(
        text("SELECT * FROM monitorventas_precio(:id_emp, :param_lista_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id, :param_limit, :param_pagina, :param_articulos, false)"),
        {"id_emp": id_emp, "param_lista_id": lista, "param_negocio_id": negocio, "param_categoria_id": categoria, "param_subcategoria_id": subcategoria, "param_limit": 0, "param_pagina": 0, "param_articulos": param_articulos}
    ).all()


def generar_excel_precios(filas) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Precios"

    encabezados = ["Negocio", "Lista", "Categoria", "Sub Categoria", "Articulo", "Descripcion", "Precio"]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        ws.append([
            fila.negocio, fila.lista, fila.categoria, fila.subcategoria,
            fila.cod_articulo, fila.nom_articulo, float(fila.precio)
        ])

    for columna in ws.columns:
        longitud = max((len(str(celda.value)) if celda.value is not None else 0) for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = longitud + 2

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer


# Historial de precio de un articulo en una lista: p_precios es el ledger
# completo (nunca promedia), asi que se lee directo sin necesitar una tabla
# "kardex" intermedia como la que si hace falta para costos (s_costovariacion).
def get_precio_historial(db: Session, id_emp: int, id_articulo: int, id_lista: int):
    result = db.execute(
        text("""
            SELECT p.fecha_mod, a.documento, a.nro_docum, p.origen,
                p.precio_anterior, p.precio_nuevo, p.usuario_mod
            FROM p_precios p
            LEFT JOIN t_ajusteprecio_lista a ON a.id_trans = p.id_trans AND a.id_articulo = p.id_articulo
            WHERE p.id_emp = :id_emp AND p.id_articulo = :id_articulo AND p.id_lista = :id_lista
            ORDER BY p.fecha_mod DESC
        """),
        {"id_emp": id_emp, "id_articulo": id_articulo, "id_lista": id_lista}
    ).all()
    return [row._mapping for row in result]
