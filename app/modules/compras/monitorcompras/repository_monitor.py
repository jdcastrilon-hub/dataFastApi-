from datetime import date

from fastapi import HTTPException
from sqlalchemy import and_, desc, text
from sqlalchemy.orm import Session, contains_eager , joinedload
from app.modules.compras.compradirecta import models
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

def get_costos(db: Session, bodega : str, negocio :str , categoria : str,subcategoria : str,page: int, size: int):
    print ("get_monitorinventario_data")
    print (size)
    stats = db.execute(text("SELECT * FROM monitorcompras_kpi_costos(:param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id )"), 
                       {"param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria , "param_subcategoria_id" : subcategoria}).first()

    # 3. Construyes el JSON de UI
    kpis = []

     #calculamos el total de registros
    total_records = stats.totalarticulos
    offset = page * size
    print (offset)
    # Llamada directa a la función de Postgres
    result = db.execute(
        text("SELECT * FROM monitorcompra_costo(:param_bodega_id, :param_negocio_id, :param_categoria_id, :param_subcategoria_id , :param_limit, :param_pagina)"),
         {"param_bodega_id": bodega, "param_negocio_id": negocio, "param_categoria_id": categoria , "param_subcategoria_id" : subcategoria , "param_limit":size,"param_pagina": offset}
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
