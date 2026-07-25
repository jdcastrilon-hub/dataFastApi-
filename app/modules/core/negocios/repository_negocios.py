from sqlalchemy import desc, or_
from sqlalchemy.orm import Session ,joinedload
from . import model_negocios, schema_negocio
from app.modules.stock.categorias import models
from app.modules.stock.tiposervicio import model_servicio

MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs: list) -> list:
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


# Obtener todas las bodegas ordenadas de mayor a menor
def get_negocios(db: Session):
    return db.query(model_negocios.Negocio).all()


# Paginacion: solo los negocios de la empresa de la sesion actual (lista de la
# pestaña Negocios de Administracion)
def get_negocios_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_negocios.Negocio).filter(model_negocios.Negocio.id_emp == id_emp)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_negocios.Negocio.cod_negocio.ilike(patron),
                model_negocios.Negocio.nom_negocio.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query.order_by(desc(model_negocios.Negocio.fecha_mod)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


# Obtener un negocio por ID, solo si pertenece a la empresa indicada
def get_negocio(db: Session, id_negocio: int, id_emp: int):
    return db.query(model_negocios.Negocio)\
        .filter(model_negocios.Negocio.id == id_negocio, model_negocios.Negocio.id_emp == id_emp)\
        .first()


def create_negocio(db: Session, obj: schema_negocio.NegocioCreate):
    logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])

    db_negocio = model_negocios.Negocio(
        id_emp=obj.id_emp,
        cod_negocio=obj.cod_negocio,
        nom_negocio=obj.nom_negocio,
        activo=obj.activo,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_negocio)
    db.commit()
    db.refresh(db_negocio)
    return db_negocio


def update_negocio(db: Session, id_negocio: int, id_emp: int, obj: schema_negocio.NegocioCreate):
    db_negocio = db.query(model_negocios.Negocio)\
        .filter(model_negocios.Negocio.id == id_negocio, model_negocios.Negocio.id_emp == id_emp)\
        .first()
    if not db_negocio:
        return None

    db_negocio.cod_negocio = obj.cod_negocio
    db_negocio.nom_negocio = obj.nom_negocio
    db_negocio.activo = obj.activo
    db_negocio.logs = _limitar_logs([log.model_dump() for log in obj.logs])
    db_negocio.fecha_mod = obj.fecha_mod

    db.commit()
    db.refresh(db_negocio)
    return db_negocio


def delete_negocio(db: Session, id_negocio: int, id_emp: int):
    db_negocio = db.query(model_negocios.Negocio)\
        .filter(model_negocios.Negocio.id == id_negocio, model_negocios.Negocio.id_emp == id_emp)\
        .first()
    if not db_negocio:
        return None

    db.delete(db_negocio)
    db.commit()
    return db_negocio

def get_negocios_con_categorias_por_empresa(db: Session, id_empresa: int):
        # 1. Obtenemos todos los negocios de la empresa
        negocios = db.query(model_negocios.Negocio).filter(model_negocios.Negocio.id_emp == id_empresa).all()

        # 2. Obtenemos todas las categorías de la empresa con sus subcategorías
        categorias = db.query(models.Categoria).filter(models.Categoria.id_emp == id_empresa).options(
                                    joinedload(models.Categoria.subcategorias)).all()
        
        tipoproducto = db.query(model_servicio.TipoServicio).filter(model_servicio.TipoServicio.id_emp == id_empresa).all()

        # 3. Mapeamos la lista de objetos Negocio al formato del DTO
        # Inyectamos la lista de categorías en cada negocio
        return {
                "idEmpresa": id_empresa,
                "nombreEmpresa": "juan",
                "listnegocio": negocios,
                "listCategorias":categorias,
                "tipoproductos":tipoproducto
        }
        