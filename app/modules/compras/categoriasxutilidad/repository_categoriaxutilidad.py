from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from . import model_categoriaxutilidad as models
from app.modules.stock.categorias import models as models_categoria

MAX_LOGS_AUDITORIA = 10


def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def get_categoriaxutilidad(db: Session, id: int):
    return (
        db.query(models.CategoriaXUtilidad)
        .options(
            joinedload(models.CategoriaXUtilidad.categoria),
            joinedload(models.CategoriaXUtilidad.subcategoria)
        )
        .filter(models.CategoriaXUtilidad.id == id)
        .first()
    )


# No se atrapa la excepcion aqui a proposito (mismo criterio que el resto del
# proyecto): si ya existe una fila "toda la categoria" o una excepcion para
# la misma subcategoria, el indice unico parcial de la migracion la rechaza y
# el manejador global de IntegrityError responde con un mensaje amigable, en
# una sola llamada de guardado.
def create_categoriaxutilidad(db: Session, obj):
    data = obj.model_dump()
    data["logs"] = _limitar_logs([log.model_dump() for log in obj.logs])
    db_obj = models.CategoriaXUtilidad(**data)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_categoriaxutilidad(db: Session, id: int, obj):
    db_obj = db.query(models.CategoriaXUtilidad).filter(models.CategoriaXUtilidad.id == id).first()
    if not db_obj:
        return None

    db_obj.id_categoria = obj.id_categoria
    db_obj.id_subcategoria = obj.id_subcategoria
    db_obj.porc_utilidad = obj.porc_utilidad
    db_obj.activo = obj.activo
    db_obj.logs = _limitar_logs([log.model_dump() for log in obj.logs])
    db_obj.fecha_mod = obj.fecha_mod

    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_categoriaxutilidad(db: Session, id: int):
    db_obj = db.query(models.CategoriaXUtilidad).filter(models.CategoriaXUtilidad.id == id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


# Paginacion (filtrada por empresa) - busqueda por nombre de categoria/subcategoria
def get_categoriaxutilidad_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = (
        db.query(models.CategoriaXUtilidad)
        .join(models_categoria.Categoria, models_categoria.Categoria.id == models.CategoriaXUtilidad.id_categoria)
        .outerjoin(models_categoria.Subcategoria, models_categoria.Subcategoria.id == models.CategoriaXUtilidad.id_subcategoria)
        .filter(models.CategoriaXUtilidad.id_emp == id_emp)
    )

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                models_categoria.Categoria.nom_categoria.ilike(patron),
                models_categoria.Subcategoria.nom_subcategoria.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = (
        query
        .options(
            joinedload(models.CategoriaXUtilidad.categoria),
            joinedload(models.CategoriaXUtilidad.subcategoria)
        )
        .order_by(desc(models.CategoriaXUtilidad.fecha_mod))
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
