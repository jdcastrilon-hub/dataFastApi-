from datetime import date
from decimal import Decimal
from io import BytesIO
from typing import Optional

from openpyxl import Workbook
from openpyxl.styles import Font
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.modules.comercial.cajas import model_cajas
from app.modules.tesoreria.catalogos.bancos import model_banco
from app.modules.comercial.mediopago import model_medio


def _fmt_money(valor) -> str:
    valor = valor or Decimal(0)
    if abs(valor) >= 1_000_000:
        return f"${valor / 1_000_000:.1f}M"
    return f"${valor:,.0f}"


def get_filtros(db: Session, id_emp: int):
    cajas = db.query(model_cajas.MCaja)\
        .filter(model_cajas.MCaja.id_emp == id_emp, model_cajas.MCaja.status == True)\
        .order_by(model_cajas.MCaja.nom_caja).all()

    bancos = db.query(model_banco.Banco)\
        .filter(model_banco.Banco.id_emp == id_emp, model_banco.Banco.activo == True)\
        .order_by(model_banco.Banco.nom_banco).all()

    mediospago = db.query(model_medio.MedioPago)\
        .filter(model_medio.MedioPago.id_emp == id_emp)\
        .order_by(model_medio.MedioPago.orden).all()

    # Dinamico a proposito (no un catalogo fijo): asi que el dia que otro proceso
    # (compras, pagos) empiece a escribir en p_movimientocajas con su propio
    # "vista", aparece solo en el filtro sin tocar backend/frontend.
    vistas_result = db.execute(
        text("SELECT DISTINCT vista FROM p_movimientocajas WHERE id_emp = :id_emp ORDER BY vista"),
        {"id_emp": id_emp}
    ).all()
    vistas = [row[0] for row in vistas_result]

    return {
        "idEmpresa": id_emp,
        "listCajas": cajas,
        "listBancos": bancos,
        "listMediosPago": mediospago,
        "listVistas": vistas
    }


def _params_movimientos(id_emp: int, fecha_inicial: Optional[date], fecha_final: Optional[date],
                         tipo_cuenta: str, id_caja: Optional[int], id_banco: Optional[int],
                         id_mediopago: Optional[int], vista: Optional[str]) -> dict:
    return {
        "id_emp": id_emp,
        "fi": fecha_inicial,
        "ff": fecha_final,
        "tipo_cuenta": tipo_cuenta,
        "id_caja": id_caja,
        "id_banco": id_banco,
        "id_mediopago": id_mediopago,
        "vista": vista
    }


def get_movimientos(db: Session, id_emp: int, fecha_inicial: Optional[date], fecha_final: Optional[date],
                     tipo_cuenta: str, id_caja: Optional[int], id_banco: Optional[int],
                     id_mediopago: Optional[int], vista: Optional[str], page: int, size: int):
    params = _params_movimientos(id_emp, fecha_inicial, fecha_final, tipo_cuenta, id_caja, id_banco, id_mediopago, vista)

    stats = db.execute(
        text("""SELECT * FROM monitortesoreria_kpi(:id_emp, :fi, :ff, :tipo_cuenta, :id_caja, :id_banco, :id_mediopago, :vista)"""),
        params
    ).first()

    # El KPI cambia de pregunta segun haya o no filtro de fecha: sin fecha es el
    # saldo actual real (tablas materializadas), con fecha es el neto del
    # periodo filtrado (calculado sobre el ledger) - ver project_data_tesoreria_module.
    if stats.con_filtro_fecha:
        kpis = [
            {"titulo": "Total Ingresos", "valor": _fmt_money(stats.total_ingresos), "icono": "trending_up", "color": "#2e7d32"},
            {"titulo": "Total Egresos", "valor": _fmt_money(stats.total_egresos), "icono": "trending_down", "color": "#c62828"},
            {"titulo": "Neto del Periodo", "valor": _fmt_money(stats.total_ingresos - stats.total_egresos), "icono": "account_balance_wallet", "color": "#1565c0"},
        ]
    else:
        kpis = [
            {"titulo": "Total en Caja", "valor": _fmt_money(stats.total_caja), "icono": "point_of_sale", "color": "#673ab7"},
            {"titulo": "Total en Banco", "valor": _fmt_money(stats.total_banco), "icono": "account_balance", "color": "#00838f"},
            {"titulo": "Total General", "valor": _fmt_money(stats.total_caja + stats.total_banco), "icono": "savings", "color": "#2e7d32"},
        ]

    total_records = stats.total_registros
    offset = page * size

    result = db.execute(
        text("""SELECT * FROM monitortesoreria_vista1(:id_emp, :fi, :ff, :tipo_cuenta, :id_caja, :id_banco, :id_mediopago, :vista, :lim, :off, true)"""),
        {**params, "lim": size, "off": offset}
    ).all()
    items = [row._mapping for row in result]

    total_pages = (total_records + size - 1) // size if size else 0

    return {
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size,
        "kpis": kpis,
        "detalles": items
    }


def get_movimientos_export_data(db: Session, id_emp: int, fecha_inicial: Optional[date], fecha_final: Optional[date],
                                 tipo_cuenta: str, id_caja: Optional[int], id_banco: Optional[int],
                                 id_mediopago: Optional[int], vista: Optional[str]):
    params = _params_movimientos(id_emp, fecha_inicial, fecha_final, tipo_cuenta, id_caja, id_banco, id_mediopago, vista)
    # param_incluir_limite=false: misma funcion y mismos filtros que la grilla paginada, pero trae todas las filas
    return db.execute(
        text("""SELECT * FROM monitortesoreria_vista1(:id_emp, :fi, :ff, :tipo_cuenta, :id_caja, :id_banco, :id_mediopago, :vista, :lim, :off, false)"""),
        {**params, "lim": 0, "off": 0}
    ).all()


def generar_excel_movimientos(filas) -> BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Movimientos Tesoreria"

    encabezados = ["Fecha", "Tipo Cuenta", "Cuenta", "Medio de Pago", "Concepto", "Vista", "Importe", "Signo"]
    ws.append(encabezados)
    for celda in ws[1]:
        celda.font = Font(bold=True)

    for fila in filas:
        cuenta = fila.nom_caja if fila.tipo_cuenta == 'CAJA' else fila.nom_banco
        ws.append([
            fila.fec_doc, fila.tipo_cuenta, cuenta, fila.tipo_mediopago, fila.concepto, fila.vista,
            float(fila.importe), fila.signo
        ])

    for columna in ws.columns:
        longitud = max((len(str(celda.value)) if celda.value is not None else 0) for celda in columna)
        ws.column_dimensions[columna[0].column_letter].width = min(longitud + 2, 40)

    ws.freeze_panes = "A2"

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
