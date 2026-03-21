from sqlalchemy import desc, text
from sqlalchemy.orm import Session, joinedload
from . import schema_reporteinventario
from app.modules.core.empresas import model_empresa
from app.modules.core.sucursales import model_sucursal


def get_empresa_by_negocios_sucursales(db: Session):
    # Traemos todo Empresa -> Negocios y Empresa -> Sucursales -> Bodegas
    empresas = db.query(model_empresa.Empresa).options(
        joinedload(model_empresa.Empresa.negocios),
        joinedload(model_empresa.Empresa.sucursales).joinedload(model_sucursal.Sucursal.bodegas)
    ).all()
    return empresas

def get_inventario_por_bodega(db: Session, bodega_id: int,page: int, size: int):

    # Calcular el desplazamiento (offset)
    offset = page * size

    # 1. Consulta para obtener el TOTAL de registros (Count)
    count_query = text("SELECT count(*) FROM reporte_inventarioxBodega(:id)")
    total_records = db.execute(count_query, {"id": bodega_id}).scalar()
    print(total_records)
    # 2. Obtener los registros de la página actual
    items = text("""
        SELECT 
            a.bodega, 
            a.cod_articulo as codarticulo, 
            a.nom_articulo as nomarticulo, 
            a.estado, 
            a.unidad, 
            a.cantidad
        FROM reporte_inventarioxBodega(:id) AS a
        ORDER BY a.cod_articulo
        LIMIT :limit OFFSET :offset
    """)

    result = db.execute(items, {
            "id": bodega_id, 
            "limit": size, 
            "offset": offset
        }).mappings().all()


    total_pages = (total_records + size - 1) // size

    return {
        "content": result,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

    
