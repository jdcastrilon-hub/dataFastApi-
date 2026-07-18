
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_usuario , esquema_usuario
from app.modules.compras.personas import modelo_personas
from app.core.auth.security import obtener_password_hash


def find_usuarios_by_query(db: Session, query: str):
    search_filter = f"%{query}%"

    return (
        db.query(
            model_usuario.Usuario.id_usuario.label("idUsuario"),
            model_usuario.Usuario.usuario.label("usuario"),
            model_usuario.Usuario.nom_usuario.label("nombreCompleto")
        )
        .filter(
            model_usuario.Usuario.activo == True,
            or_(
                model_usuario.Usuario.usuario.ilike(search_filter),
                model_usuario.Usuario.nom_usuario.ilike(search_filter)
            )
        )
        .order_by(model_usuario.Usuario.nom_usuario)
        .limit(20)
        .all()
    )


# Crear un proveedor
def create_usuario(db: Session, obj: esquema_usuario.UsuarioCreate):
        print("--- CONTROL DE DATOS ---")
        print(f"Tipo de obj.clave: {type(obj.clave)}")
        print(f"Contenido de obj.clave: {obj.clave}")
        print("------------------------")
        # Convertimos la lista de objetos LogEntry a una lista de diccionarios
        logs_dict = [log.model_dump() for log in obj.logs]
        # Inicializamos la variable que contendrá el ID de la persona definitiva
        persona_id_final = obj.id_persona

        clave_segura = obtener_password_hash(obj.clave)

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

        # 2. Crear Usuario
        bd_usuario = model_usuario.Usuario(
            usuario=obj.usuario,
            clave=clave_segura,
            id_persona=persona_id_final,
            nom_usuario=obj.nom_usuario,
            activo=obj.activo,           
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_usuario)

        db.flush() # Envio a base de datos
        db.commit()
        db.refresh(bd_usuario)

        return bd_usuario
