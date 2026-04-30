
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session
from . import model_cliente , schema_cliente
from app.modules.compras.personas import modelo_personas


# Crear un proveedor
def create_cliente(db: Session, obj: schema_cliente.ClienteCreate):
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
        bd_cliente = model_cliente.Cliente(
            id_emp=obj.id_emp,
            id_persona=persona_id_final,
            cod_tit=obj.cod_tit,
            nom_cliente=obj.nom_cliente,
            direccion=obj.direccion,
            activo=obj.activo,
            mail=obj.mail,
            observacion=obj.observacion,
            logs=logs_dict,
            fecha_mod=obj.fecha_mod
        )
        db.add(bd_cliente)

        db.flush() # Envio a base de datos
        db.commit()
        db.refresh(bd_cliente)

        return bd_cliente
