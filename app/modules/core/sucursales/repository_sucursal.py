from sqlalchemy import and_, desc, or_
from sqlalchemy.orm import Session, contains_eager, joinedload
from . import model_sucursal, schema_sucursal
from app.modules.stock.bodegas import model_bodega
from app.modules.comercial.documentos import model_docum
from app.modules.comercial.mediopago import model_medio
from app.modules.comercial.cajas import model_cajas
from app.modules.core.usuarios import model_usuario

MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs: list) -> list:
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def get_sucursales(db: Session, page: int = 0, size: int = 100):
    print(page)
    return db.query(model_sucursal.Sucursal).offset(page).limit(size).all()


# Paginacion: solo las sucursales de la empresa de la sesion actual (lista de la
# pestaña Sucursales de Administracion - distinto de get_sucursales, que sigue
# siendo el usado por /list y /combo para otros modulos).
def get_sucursales_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_sucursal.Sucursal).filter(model_sucursal.Sucursal.id_emp == id_emp)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_sucursal.Sucursal.cod_sucursal.ilike(patron),
                model_sucursal.Sucursal.nom_sucursal.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query.order_by(desc(model_sucursal.Sucursal.fecha_mod)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


# Obtener una sucursal por ID, solo si pertenece a la empresa indicada (con sus usuarios asignados)
def get_sucursal(db: Session, id_sucursal: int, id_emp: int):
    return db.query(model_sucursal.Sucursal)\
        .options(joinedload(model_sucursal.Sucursal.usuarios).joinedload(model_sucursal.SucursalXUsuario.usuario))\
        .filter(model_sucursal.Sucursal.id == id_sucursal, model_sucursal.Sucursal.id_emp == id_emp)\
        .first()

def get_sucursales_by_bodegas(db: Session, id_empresa: int):
    # 1. Traemos las sucursales y cargamos sus bodegas relacionadas en una sola consulta
    sucursales = db.query(model_sucursal.Sucursal)\
        .options(joinedload(model_sucursal.Sucursal.bodegas))\
        .filter(model_sucursal.Sucursal.id_emp == id_empresa)\
        .all()
    
    mediopago = db.query(model_medio.MedioPago).order_by(model_medio.MedioPago.orden).all()
    
    # 2. Mapeamos directamente
    resultado = []
    for sucursal in sucursales:
        #Documentos de la empresa y sucursal
        documentos = db.query(model_docum.DocumentoVenta)\
        .filter(model_docum.DocumentoVenta.id_emp == id_empresa,
                model_docum.DocumentoVenta.id_sucursal_emp == sucursal.id)\
        .all()

        

        resultado.append({
            "id": sucursal.id,
            "idEmpresa": sucursal.id_emp,
            "codSucursal": sucursal.cod_sucursal,
            "nomSucursal": sucursal.nom_sucursal,
            "list_bodegas": sucursal.bodegas,
            "documentos":documentos,
            "mediopago":mediopago
        })
            
    return resultado


def get_sucursales_by_cajas(db: Session, id_empresa: int, usuario: str = None):

    query = (
            db.query(model_sucursal.Sucursal)
            # 1. Aquí haces el JOIN usando la relación de tu modelo
            .join(model_sucursal.Sucursal.caja)
            # 2. Le indicas a SQLAlchemy que use este mismo JOIN para mapear los objetos hijos
            .options(contains_eager(model_sucursal.Sucursal.caja))
            # 3. Aplicas los filtros usando directamente la clase del modelo de la caja (MCaja)
            .filter(
                and_(
                    model_sucursal.Sucursal.id_emp == id_empresa,
                    model_sucursal.Sucursal.activo == True,
                    # CORRECCIÓN: Usamos la clase MCaja directamente.
                    # SQLAlchemy es inteligente y sabe que se refiere al JOIN de arriba.
                    model_cajas.MCaja.cajapos == True
                )
            )
        )

    if usuario:
        # Solo las cajas POS que este usuario tiene asociadas en m_cajasxuser
        # (ej. para abrir turno: no debe poder elegir una caja ajena).
        cajas_del_usuario = (
            db.query(model_cajas.MCajasXUser.id_caja)
            .join(model_usuario.Usuario, model_usuario.Usuario.id_usuario == model_cajas.MCajasXUser.id_usuario)
            .filter(model_usuario.Usuario.usuario == usuario)
        )
        query = query.filter(model_cajas.MCaja.id.in_(cajas_del_usuario))

    sucursales = query.all()

   # Mapeamos manualmente el atributo de la relación si el nombre difiere.
    # En tu modelo pusiste: caja = relationship("MCaja", back_populates="sucursal")
    # Pero el JSON espera la propiedad llamada 'cajas'. Hacemos el mapeo rápido:
    for s in sucursales:
        s.cajas = s.caja  # Asignamos la lista de MCaja al atributo virtual 'cajas' que pide Pydantic
        
    return sucursales

def create_sucursal(db: Session, obj: schema_sucursal.SucursalCreate):
    logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])

    db_sucursal = model_sucursal.Sucursal(
        id_emp=obj.id_emp,
        cod_sucursal=obj.cod_sucursal,
        nom_sucursal=obj.nom_sucursal,
        id_ciudad=obj.id_ciudad,
        direccion=obj.direccion,
        telefono=obj.telefono,
        activo=obj.activo,
        logs=logs_dict,
        fecha_mod=obj.fecha_mod
    )
    db.add(db_sucursal)
    db.flush()

    for usuario in obj.usuarios:
        db.add(model_sucursal.SucursalXUsuario(id_sucursal=db_sucursal.id, id_usuario=usuario.id_usuario))

    db.commit()
    db.refresh(db_sucursal)
    return db_sucursal


def update_sucursal(db: Session, id_sucursal: int, id_emp: int, obj: schema_sucursal.SucursalCreate):
    db_sucursal = db.query(model_sucursal.Sucursal)\
        .filter(model_sucursal.Sucursal.id == id_sucursal, model_sucursal.Sucursal.id_emp == id_emp)\
        .first()
    if not db_sucursal:
        return None

    db_sucursal.cod_sucursal = obj.cod_sucursal
    db_sucursal.nom_sucursal = obj.nom_sucursal
    db_sucursal.id_ciudad = obj.id_ciudad
    db_sucursal.direccion = obj.direccion
    db_sucursal.telefono = obj.telefono
    db_sucursal.activo = obj.activo
    db_sucursal.logs = _limitar_logs([log.model_dump() for log in obj.logs])
    db_sucursal.fecha_mod = obj.fecha_mod

    # Reemplaza los usuarios asignados (borrar e reinsertar, igual que roles/conceptos)
    db.query(model_sucursal.SucursalXUsuario).filter(model_sucursal.SucursalXUsuario.id_sucursal == id_sucursal).delete()
    db.flush()
    for usuario in obj.usuarios:
        db.add(model_sucursal.SucursalXUsuario(id_sucursal=id_sucursal, id_usuario=usuario.id_usuario))

    db.commit()
    db.refresh(db_sucursal)
    return db_sucursal


def delete_sucursal(db: Session, id_sucursal: int, id_emp: int):
    db_sucursal = db.query(model_sucursal.Sucursal)\
        .filter(model_sucursal.Sucursal.id == id_sucursal, model_sucursal.Sucursal.id_emp == id_emp)\
        .first()
    if not db_sucursal:
        return None

    db.delete(db_sucursal)  # cascade borra m_userxsucursal
    db.commit()
    return db_sucursal