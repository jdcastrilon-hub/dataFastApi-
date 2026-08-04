from sqlalchemy import desc, text
from sqlalchemy.orm import Session , joinedload
from sqlalchemy.exc import IntegrityError, DataError
from . import model_empresa, schema_empresa
from app.exceptions import TransaccionValidationError
from app.modules.core.roles import model_rol
from app.modules.core.usuarios import model_usuario

MAX_LOGS_AUDITORIA = 10

def _limitar_logs(logs: list) -> list:
    if not logs:
        return logs
    return logs[-MAX_LOGS_AUDITORIA:]


# Obtener todas las bodegas ordenadas de mayor a menor
def get_empresas(db: Session):
    return db.query(model_empresa.Empresa).all()

def get_empresasByNegocios(db: Session):
    return db.query(model_empresa.Empresa).options(
        joinedload(model_empresa.Empresa.negocios)).all()


# "Mi Empresa" (Administracion): un solo registro, el de la empresa activa.
def get_empresa(db: Session, id_emp: int):
    return db.query(model_empresa.Empresa).filter(model_empresa.Empresa.id_emp == id_emp).first()


def update_empresa_perfil(db: Session, id_emp: int, obj):
    db_empresa = get_empresa(db, id_emp)
    if not db_empresa:
        return None

    # Solo los campos de perfil - id_shard/id_plan nunca se tocan aqui, ni
    # siquiera si vinieran en el payload (no forman parte de EmpresaPerfilUpdate).
    db_empresa.nom_emp = obj.nom_emp
    db_empresa.razon_social = obj.razon_social
    db_empresa.cod_doc = obj.cod_doc
    db_empresa.nit = obj.nit
    db_empresa.direccion = obj.direccion
    db_empresa.cod_ciudad = obj.cod_ciudad
    db_empresa.telefono = obj.telefono
    db_empresa.correo = obj.correo
    db_empresa.logs = _limitar_logs([log.model_dump() for log in obj.logs])
    db_empresa.fecha_mod = obj.fecha_mod

    db.commit()
    db.refresh(db_empresa)
    return db_empresa


# Provisioning: crea la empresa, su rol superadmin, asocia un usuario YA
# EXISTENTE (nunca se crea uno aqui) y carga los 4 maestros base (via
# sp_core_nuevaempresa) - todo en una sola transaccion. Ver
# docs/tecnica/specs/core/creacion-empresa.md.
def create_empresa(db: Session, obj: schema_empresa.EmpresaCreate):
    try:
        bd_empresa = model_empresa.Empresa(
            nom_emp=obj.nom_emp,
            razon_social=obj.razon_social,
            cod_doc=obj.cod_doc,
            nit=obj.nit,
            direccion=obj.direccion,
            cod_ciudad=obj.cod_ciudad,
            telefono=obj.telefono,
            correo=obj.correo,
            activa=True,
            logs=_limitar_logs([log.model_dump() for log in obj.logs]),
            fecha_mod=obj.fecha_mod,
        )
        db.add(bd_empresa)
        db.flush()  # necesitamos bd_empresa.id_emp

        bd_rol = model_rol.Rol(
            id_emp=bd_empresa.id_emp,
            codigo="SUPERADMIN",
            nombre="Superadmin",
            descripcion="Rol de administracion total, creado automaticamente al provisionar la empresa",
            activo=True,
            es_superadmin=True,
        )
        db.add(bd_rol)
        db.flush()  # necesitamos bd_rol.id_rol

        # El usuario administrador debe preexistir - no se crea aqui ni se
        # pre-valida (una sola llamada de guardado que falla con mensaje claro,
        # no verificaciones aparte). Si no existe, id_usuario queda None y el
        # NOT NULL de md_empresaxuser/md_usuarioxrol lo rechaza mas abajo.
        usuario_db = db.query(model_usuario.Usuario).filter(
            model_usuario.Usuario.usuario == obj.usuario
        ).first()
        id_usuario = usuario_db.id_usuario if usuario_db else None

        db.add(model_empresa.EmpresaXUser(id_usuario=id_usuario, id_emp=bd_empresa.id_emp, activo=True))
        db.add(model_rol.RolXUsuario(id_usuario=id_usuario, id_rol=bd_rol.id_rol))

        # Catalogos base de arranque (estados/unidades/motivos de ajuste/tipos de
        # servicio) - valores fijos definidos en el SP, no una copia de otra
        # empresa (ver migracion 433c60103665_agregar_sp_core_nuevaempresa).
        db.execute(text("CALL public.sp_core_nuevaempresa(:id_emp)"), {"id_emp": bd_empresa.id_emp})

        db.commit()
        db.refresh(bd_empresa)
        return bd_empresa
    except (IntegrityError, DataError):
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise TransaccionValidationError(str(e))