from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_proveedor , schema_proveedor
from app.modules.compras.personas import modelo_personas

# Obtener todas las bodegas ordenadas de mayor a menor
def get_proveedor(db: Session):
    return db.query(model_proveedor.Proveedor).all()

#Paginacion
def get_proveedor_paginated(db: Session, page: int, size: int):
    # 1. Contar el total de registros en la tabla
    total_records = db.query(model_proveedor.Proveedor).count()
    
    # 2. Obtener los registros de la página actual
    offset = page * size
    items = db.query(model_proveedor.Proveedor).order_by(desc(model_proveedor.Proveedor.fecha_mod)).offset(offset).limit(size).all()
    
    # 3. Calcular total de páginas
    total_pages = (total_records + size - 1) // size
    
    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }

def find_proveedores_by_query(db: Session, query: str):
        # Creamos el patrón para el LIKE: %query%
        search_filter = f"%{query}%"
        
        return (
            db.query(
                model_proveedor.Proveedor.id_proveedor.label("idProveedor"),
                model_proveedor.Proveedor.id_persona.label("idPersona"),
                model_proveedor.Proveedor.cod_tit.label("codTit"),
                model_proveedor.Proveedor.razon_social.label("nombreCompleto")
            )
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
        logs_dict = [log.model_dump() for log in obj.logs]
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