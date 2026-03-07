from sqlalchemy import or_
from sqlalchemy.orm import Session
from . import model_proveedor , schema_proveedor
from app.modules.compras.personas import modelo_personas

# Obtener todas las bodegas ordenadas de mayor a menor
def get_proveedor(db: Session):
    return db.query(model_proveedor.Proveedor).all()

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

        # 2. Crear proveedor
        bd_proveedor = model_proveedor.Proveedor(
            id_persona=bd_persona.id_persona,
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
        db.refresh(bd_persona)

        return bd_persona
    
    except Exception as e:
            db.rollback() 
            raise e      