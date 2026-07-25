from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload
from app.modules.core.sucursales import model_sucursal


def get_filtros(db: Session, id_empresa: int):
    sucursales = db.query(model_sucursal.Sucursal)\
        .options(joinedload(model_sucursal.Sucursal.caja))\
        .filter(model_sucursal.Sucursal.id_emp == id_empresa)\
        .all()

    return {
        "idEmpresa": id_empresa,
        "listsucursales": sucursales
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
