from sqlalchemy import desc, or_
from sqlalchemy.orm import Session, joinedload
from . import model_usuario, esquema_usuario
from app.modules.compras.personas import modelo_personas
from app.modules.core.empresas.model_empresa import EmpresaXUser
from app.core.auth.security import obtener_password_hash

# Máximo de entradas de auditoría que se conservan en el jsonb "logs".
MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs):
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


def find_usuarios_by_query(db: Session, query: str, id_emp: int):
    search_filter = f"%{query}%"

    return (
        db.query(
            model_usuario.Usuario.id_usuario.label("idUsuario"),
            model_usuario.Usuario.usuario.label("usuario"),
            model_usuario.Usuario.nom_usuario.label("nombreCompleto")
        )
        # Solo usuarios asociados a la empresa actual (via md_empresaxuser) - este
        # combo se usa para asignar usuarios a roles/sucursales/cajas/conceptos, y
        # asignarle algo de otra empresa a un usuario que nunca perteneció a ella
        # no tiene sentido.
        .join(EmpresaXUser, EmpresaXUser.id_usuario == model_usuario.Usuario.id_usuario)
        .filter(
            model_usuario.Usuario.activo == True,
            EmpresaXUser.id_emp == id_emp,
            or_(
                model_usuario.Usuario.usuario.ilike(search_filter),
                model_usuario.Usuario.nom_usuario.ilike(search_filter)
            )
        )
        .order_by(model_usuario.Usuario.nom_usuario)
        .limit(20)
        .all()
    )


# Obtener un usuario por ID, solo si pertenece a la empresa indicada (con su persona asociada)
def get_usuario(db: Session, usuario_id: int, id_emp: int):
    return db.query(model_usuario.Usuario)\
        .join(EmpresaXUser, EmpresaXUser.id_usuario == model_usuario.Usuario.id_usuario)\
        .options(joinedload(model_usuario.Usuario.persona))\
        .filter(
            model_usuario.Usuario.id_usuario == usuario_id,
            EmpresaXUser.id_emp == id_emp
        ).first()


# Paginacion: solo usuarios asociados (via md_empresaxuser) a la empresa indicada
def get_usuario_paginated(db: Session, page: int, size: int, id_emp: int, texto: str = None):
    query = db.query(model_usuario.Usuario)\
        .join(EmpresaXUser, EmpresaXUser.id_usuario == model_usuario.Usuario.id_usuario)\
        .filter(EmpresaXUser.id_emp == id_emp)

    if texto:
        patron = f"%{texto}%"
        query = query.filter(
            or_(
                model_usuario.Usuario.usuario.ilike(patron),
                model_usuario.Usuario.nom_usuario.ilike(patron)
            )
        )

    total_records = query.count()

    offset = page * size
    items = query.order_by(desc(model_usuario.Usuario.fecha_mod)).offset(offset).limit(size).all()

    total_pages = (total_records + size - 1) // size

    return {
        "content": items,
        "totalElements": total_records,
        "totalPages": total_pages,
        "number": page,
        "size": size
    }


# Crear un usuario: registra md_usuarios y lo asocia a la empresa via md_empresaxuser
def create_usuario(db: Session, obj: esquema_usuario.UsuarioCreate):
    logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])
    persona_id_final = obj.id_persona

    # La clave es NOT NULL en la BD: si viene vacia, se deja en None a proposito para
    # que el manejador global de IntegrityError devuelva un mensaje amigable (sin
    # necesidad de una validacion previa por separado).
    clave_segura = obtener_password_hash(obj.clave) if obj.clave else None

    if obj.id_persona == 0:
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
        db.flush()
        persona_id_final = bd_persona.id_persona

    # 2. Crear usuario
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
    db.flush()

    # 3. Asociar el usuario a la empresa actual
    bd_empresaxuser = EmpresaXUser(
        id_usuario=bd_usuario.id_usuario,
        id_emp=obj.id_emp,
        activo=True
    )
    db.add(bd_empresaxuser)

    db.commit()
    db.refresh(bd_usuario)

    return bd_usuario


# Actualizar un usuario existente. Tambien actualiza los datos propios de la persona
# ligada (misma logica que proveedores: no se permite reasignar a otra persona desde
# aqui, solo corregir los datos de la que ya esta ligada). La asociacion a empresa
# (md_empresaxuser) no se toca aqui, se fija solo al crear.
def update_usuario(db: Session, usuario_id: int, obj: esquema_usuario.UsuarioCreate):
    db_query = db.query(model_usuario.Usuario).filter(model_usuario.Usuario.id_usuario == usuario_id)
    db_usuario = db_query.first()

    if db_usuario:
        logs_dict = _limitar_logs([log.model_dump() for log in obj.logs])

        valores = {
            "usuario": obj.usuario,
            "nom_usuario": obj.nom_usuario,
            "activo": obj.activo,
            "logs": logs_dict,
            "fecha_mod": obj.fecha_mod
        }
        # Clave en blanco = no cambiarla
        if obj.clave:
            valores["clave"] = obtener_password_hash(obj.clave)

        db_query.update(valores, synchronize_session=False)

        if obj.persona:
            db.query(modelo_personas.Persona)\
                .filter(modelo_personas.Persona.id_persona == db_usuario.id_persona)\
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
        db.refresh(db_usuario)
    return db_usuario
