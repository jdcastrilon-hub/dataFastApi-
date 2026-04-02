from datetime import date

from fastapi import HTTPException
from sqlalchemy import and_, desc, text
from sqlalchemy.orm import Session, contains_eager , joinedload
from app.modules.compras.proveedores import model_proveedor
from app.modules.compras.compradirecta import models



def get_monitorcomprasrealizadas_data(db: Session, fechainicial : date, fechafinal :date , id_bodega : int, id_proveedor :int,articulo :int ,page: int, size: int):
    print ("get_monitorcomprasrealizadas_data")
    print (size)
    stats = db.execute(text("SELECT * FROM monitorCompras_KPI(:fechainicial, :fechafinal, :bodega, :proveedor , :articulo)"), 
                      {"fechainicial": fechainicial, "fechafinal": fechafinal, "bodega": id_bodega , "proveedor" : id_proveedor , "articulo" : articulo}).first()
    print (stats)
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
    print (offset)
    # Llamada directa a la función de Postgres
    result = db.execute(
        text("SELECT * FROM monitorcompras_vista1(:fechainicial, :fechafinal, :bodega, :proveedor , :articulo, :lim, :off)"),
         {"fechainicial": fechainicial, "fechafinal": fechafinal, "bodega": id_bodega , "proveedor" : id_proveedor , "articulo" : articulo,"lim":size,"off": offset}
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

