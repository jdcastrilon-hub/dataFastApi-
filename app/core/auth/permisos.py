from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.modules.core.roles.model_rol import Rol, RolXUsuario
from app.modules.core.roles.repository_rol import usuario_es_superadmin
from app.modules.core.permisos.model_permiso import RolPermiso, MenuPermiso, Permiso
from app.modules.core.permisos.repository_permiso import modulo_habilitado_para_empresa
from app.modules.core.menus.model_menu import Menu

"""
Chequeo de autorizacion a nivel de accion (Crear/Editar/Eliminar), para usar en
los endpoints que hacen una transaccion en la BD (save/edit/delete). Los
endpoints de solo lectura (pagination/search) NO llevan este chequeo a
proposito - alcanza con esconder los botones en el frontend (PermisosStateService),
ya que leer no modifica nada.
"""

def usuario_tiene_permiso(db: Session, id_usuario: int, id_emp: int, menu_codigo: str, accion: str) -> bool:
    if usuario_es_superadmin(db, id_usuario, id_emp):
        return True

    # El chequeo de modulo aplica solo a roles no-superadmin: el unico que
    # activa/desactiva modulos es el superadmin de la propia empresa, asi que
    # nunca deberia quedar el mismo bloqueado por su propia decision (ver
    # docs/tecnica/specs/core/delegacion-permisos-menu-exclusivo.md).
    menu = db.query(Menu).filter(Menu.codigo == menu_codigo).first()
    if menu and not modulo_habilitado_para_empresa(db, id_emp, menu.id_modulo):
        return False

    return db.query(RolPermiso)\
        .join(RolXUsuario, RolXUsuario.id_rol == RolPermiso.id_rol)\
        .join(Rol, Rol.id_rol == RolPermiso.id_rol)\
        .join(MenuPermiso, MenuPermiso.id_menu_permiso == RolPermiso.id_menu_permiso)\
        .join(Menu, Menu.id_menu == MenuPermiso.id_menu)\
        .join(Permiso, Permiso.id_permiso == MenuPermiso.id_permiso)\
        .filter(
            RolXUsuario.id_usuario == id_usuario,
            Rol.id_emp == id_emp,
            Rol.activo == True,
            Menu.codigo == menu_codigo,
            Permiso.codigo == accion
        ).first() is not None


def verificar_permiso(db: Session, id_usuario: int, id_emp: int, menu_codigo: str, accion: str) -> None:
    if not usuario_tiene_permiso(db, id_usuario, id_emp, menu_codigo, accion):
        raise HTTPException(status_code=403, detail="No tienes permiso para realizar esta acción")
