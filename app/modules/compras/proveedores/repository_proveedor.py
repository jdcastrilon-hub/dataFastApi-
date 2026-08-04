from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from . import model_proveedor , schema_proveedor
from app.modules.compras.personas import modelo_personas

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]

# Obtener todos los proveedores
def get_proveedores(db: Session):
    return db.query(model_proveedor.Proveedor).all()

# Obtener un proveedor por ID (con la persona asociada, para ver/editar)
def get_proveedor(db: Session, proveedor_id: int):
    return db.query(model_proveedor.Proveedor)\
        .options(joinedload(model_proveedor.Proveedor.persona))\
        .filter(model_proveedor.Proveedor.id_proveedor == proveedor_id).first()

#Paginacion (filtrada por empresa)
def get_proveedor_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_proveedor.Proveedor).filter(model_proveedor.Proveedor.id_emp == id_emp)

    # Filtro de busqueda por documento o razon social (si el usuario escribio algo)
    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_proveedor.Proveedor.cod_tit.ilike(patron),
                model_proveedor.Proveedor.razon_social.ilike(patron)
            )
        )

    # 1. Contar el total de registros que cumplen el filtro
    total_records = query.count()

    # 2. Obtener los registros de la página actual
    offset = page * size
    items = query.order_by(desc(model_proveedor.Proveedor.fecha_mod)).offset(offset).limit(size).all()

    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

def find_proveedores_by_query(db: Session, id_emp: int, query: str):
        # Creamos el patrón para el LIKE: %query%
        search_filter = f"%{query}%"

        return (
            db.query(
                model_proveedor.Proveedor.id_proveedor.label("idProveedor"),
                model_proveedor.Proveedor.id_persona.label("idPersona"),
                model_proveedor.Proveedor.cod_tit.label("codTit"),
                model_proveedor.Proveedor.razon_social.label("nombreCompleto")
            )
            .filter(model_proveedor.Proveedor.id_emp == id_emp)
            .filter(
                or_(
                    model_proveedor.Proveedor.cod_tit.ilike(search_filter),
                    model_proveedor.Proveedor.razon_social.ilike(search_filter)
                )
            )
            .order_by(model_proveedor.Proveedor.razon_social)
            .limit(20)
            .all()
        )


# Crear un proveedor
def create_proveedor(db: Session, obj: schema_proveedor.ProveedorCreate):
    try:
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
        # Inicializamos la variable que contendrá el ID de la persona definitiva
        persona_id_final = obj.id_persona

        if(obj.id_persona==0):
            # 1. Crear persona
            bd_persona = modelo_personas.Persona(            
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
            db.flush() # Envio a base de datos
            # Actualizamos el ID final con el nuevo ID generado
            persona_id_final = bd_persona.id_persona

        # 2. Crear proveedor
        bd_proveedor = model_proveedor.Proveedor(
            id_emp=obj.id_emp,
            id_persona=persona_id_final,
            cod_tit=obj.cod_tit,
            razon_social=obj.razon_social,
            regimen=obj.regimen,
            activo=obj.activo,
            observacion=obj.observacion,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_proveedor)

        db.flush() # Envio a base de datos
        db.commit()
        db.refresh(bd_proveedor)

        return bd_proveedor

    except Exception as e:
            db.rollback()
            raise e

# Actualizar un proveedor existente. Tambien actualiza los datos propios de la
# persona ligada (no se permite reasignar a otra persona desde aqui, solo corregir
# los datos de la que ya esta ligada): al no existir todavia un maestro de personas
# dedicado, esta es la unica pantalla donde se pueden corregir esos datos.
def update_proveedor(db: Session, proveedor_id: int, obj: schema_proveedor.ProveedorCreate):
    db_query = db.query(model_proveedor.Proveedor).filter(model_proveedor.Proveedor.id_proveedor == proveedor_id)
    db_proveedor = db_query.first()

    if db_proveedor:
        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
        db_query.update({
            "cod_tit": obj.cod_tit,
            "razon_social": obj.razon_social,
            "regimen": obj.regimen,
            "activo": obj.activo,
            "observacion": obj.observacion,
            "logs": logs_dict,
            "fecha_mod": obj.fecha_mod
        }, synchronize_session=False)

        if obj.persona:
            db.query(modelo_personas.Persona)\
                .filter(modelo_personas.Persona.id_persona == db_proveedor.id_persona)\
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
        db.refresh(db_proveedor)
    return db_proveedor

# Eliminar un proveedor (la persona asociada se conserva, puede seguir referenciada
# por compras historicas o reutilizarse en clientes/empleados)
def delete_proveedor(db: Session, proveedor_id: int):
    db_proveedor = db.query(model_proveedor.Proveedor).filter(model_proveedor.Proveedor.id_proveedor == proveedor_id).first()
    if db_proveedor:
        db.delete(db_proveedor)
        db.commit()
    return db_proveedor