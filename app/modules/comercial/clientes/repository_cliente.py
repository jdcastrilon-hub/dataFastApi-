from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from . import model_cliente, schema_cliente
from app.modules.compras.personas import modelo_personas

MAX_LOGS_AUDITORIA = 10


def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def find_clientes_by_query(db: Session, id_emp: int, query: str):
    search_filter = f"%{query}%"

    return (
        db.query(
            model_cliente.Cliente.id_cliente.label("idCliente"),
            model_cliente.Cliente.id_persona.label("idPersona"),
            model_cliente.Cliente.cod_tit.label("codTit"),
            model_cliente.Cliente.nom_cliente.label("nombreCompleto")
        )
        .filter(model_cliente.Cliente.id_emp == id_emp)
        .filter(
            or_(
                model_cliente.Cliente.cod_tit.ilike(search_filter),
                model_cliente.Cliente.nom_cliente.ilike(search_filter)
            )
        )
        .order_by(model_cliente.Cliente.nom_cliente)
        .limit(20)
        .all()
    )


# Obtener un cliente por ID (con la persona asociada, para ver/editar)
def get_cliente(db: Session, cliente_id: int):
    return db.query(model_cliente.Cliente)\
        .options(joinedload(model_cliente.Cliente.persona))\
        .filter(model_cliente.Cliente.id_cliente == cliente_id).first()


# Paginacion (filtrada por empresa)
def get_cliente_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_cliente.Cliente).filter(model_cliente.Cliente.id_emp == id_emp)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_cliente.Cliente.cod_tit.ilike(patron),
                model_cliente.Cliente.nom_cliente.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query.order_by(desc(model_cliente.Cliente.fecha_mod)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


# Crear un cliente
def create_cliente(db: Session, obj: schema_cliente.ClienteCreate):
    try:
        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
        persona_id_final = obj.id_persona

        if not obj.id_persona:
            # 1. Crear persona
            bd_persona = modelo_personas.Persona(
                id_emp=obj.id_emp,
                id_tipodoc=obj.persona.id_tipodoc,
                cod_tit=obj.persona.cod_tit,
                nombres=obj.persona.nombres,
                apellidos=obj.persona.apellidos,
                nombre_completo=obj.persona.nombre_completo,
                sexo=obj.persona.sexo,
                fec_nacimiento=obj.persona.fec_nacimiento,
                direccion=obj.persona.direccion,
                telefono=obj.persona.telefono,
                mail=obj.persona.mail,
                id_ciudad=obj.persona.id_ciudad,
                logs=logs_dict,
                fecha_mod=obj.fecha_mod
            )
            db.add(bd_persona)
            db.flush()
            persona_id_final = bd_persona.id_persona

        # 2. Crear cliente
        bd_cliente = model_cliente.Cliente(
            id_emp=obj.id_emp,
            id_persona=persona_id_final,
            cod_tit=obj.cod_tit,
            nom_cliente=obj.nom_cliente,
            direccion=obj.direccion,
            mail=obj.mail,
            activo=obj.activo,
            observacion=obj.observacion,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_cliente)

        db.flush()
        db.commit()
        db.refresh(bd_cliente)

        return bd_cliente

    except Exception as e:
        db.rollback()
        raise e


# Actualizar un cliente existente. Tambien actualiza los datos propios de la
# persona ligada (no se permite reasignar a otra persona desde aqui, solo corregir
# los datos de la que ya esta ligada) - mismo criterio que Proveedores.
def update_cliente(db: Session, cliente_id: int, obj: schema_cliente.ClienteCreate):
    db_query = db.query(model_cliente.Cliente).filter(model_cliente.Cliente.id_cliente == cliente_id)
    db_cliente = db_query.first()

    if db_cliente:
        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
        db_query.update({
            "cod_tit": obj.cod_tit,
            "nom_cliente": obj.nom_cliente,
            "direccion": obj.direccion,
            "mail": obj.mail,
            "activo": obj.activo,
            "observacion": obj.observacion,
            "logs": logs_dict,
            "fecha_mod": obj.fecha_mod
        }, synchronize_session=False)

        if obj.persona:
            db.query(modelo_personas.Persona)\
                .filter(modelo_personas.Persona.id_persona == db_cliente.id_persona)\
                .update({
                    "id_tipodoc": obj.persona.id_tipodoc,
                    "cod_tit": obj.persona.cod_tit,
                    "nombres": obj.persona.nombres,
                    "apellidos": obj.persona.apellidos,
                    "nombre_completo": obj.persona.nombre_completo,
                    "sexo": obj.persona.sexo,
                    "fec_nacimiento": obj.persona.fec_nacimiento,
                    "direccion": obj.persona.direccion,
                    "telefono": obj.persona.telefono,
                    "mail": obj.persona.mail,
                    "id_ciudad": obj.persona.id_ciudad,
                    "fecha_mod": obj.fecha_mod
                }, synchronize_session=False)

        db.commit()
        db.refresh(db_cliente)
    return db_cliente


# Eliminar un cliente (la persona asociada se conserva, puede seguir referenciada
# por otros modulos o reutilizarse en proveedores/empleados)
def delete_cliente(db: Session, cliente_id: int):
    db_cliente = db.query(model_cliente.Cliente).filter(model_cliente.Cliente.id_cliente == cliente_id).first()
    if db_cliente:
        db.delete(db_cliente)
        db.commit()
    return db_cliente
