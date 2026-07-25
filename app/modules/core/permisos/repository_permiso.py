from sqlalchemy.orm import Session
from . import model_permiso
from app.modules.core.menus.model_menu import Menu
from app.modules.core.roles.model_rol import Rol, RolXUsuario
from app.modules.core.roles.repository_rol import usuario_es_superadmin

# Orden fijo de columnas de la matriz (Ver/Crear/Editar/Buscar/Eliminar)
ORDEN_ACCIONES = ['VER', 'CREAR', 'EDITAR', 'BUSCAR', 'ELIMINAR']


def get_modulos_combo(db: Session):
    return db.query(model_permiso.Modulo)\
        .filter(model_permiso.Modulo.activo == True)\
        .order_by(model_permiso.Modulo.orden)\
        .all()


# Roles superadmin quedan excluidos de este combo SIEMPRE, incluso para un
# superadmin - a diferencia del maestro de Roles (donde si tiene sentido verlo,
# para gestionar quien mas tiene ese rol), aca nunca hay nada que configurar:
# el flag ignora md_rol_permiso por completo, no importa quien mire.
def get_roles_combo(db: Session, id_emp: int):
    return db.query(Rol)\
        .filter(Rol.id_emp == id_emp, Rol.activo == True, Rol.es_superadmin == False)\
        .order_by(Rol.nombre)\
        .all()


# Devuelve True si el rol existe, pertenece a la empresa indicada, y NO es
# superadmin (la matriz nunca aplica a un rol superadmin, para nadie - editar
# sus checkboxes no cambiaria nada ya que el flag salta ese chequeo).
def rol_pertenece_a_empresa(db: Session, id_rol: int, id_emp: int) -> bool:
    return db.query(Rol).filter(
        Rol.id_rol == id_rol, Rol.id_emp == id_emp, Rol.es_superadmin == False
    ).first() is not None


def get_matriz(db: Session, id_rol: int, id_modulo: int):
    # Formularios reales del modulo (con ruta propia, no los contenedores tipo
    # "Maestros"/"Transacciones" que no tienen acciones propias).
    formularios = db.query(Menu)\
        .filter(Menu.id_modulo == id_modulo, Menu.activo == True, Menu.ruta.isnot(None), Menu.ruta != '')\
        .order_by(Menu.orden)\
        .all()

    if not formularios:
        return []

    ids_menu = [f.id_menu for f in formularios]

    menu_permisos = db.query(model_permiso.MenuPermiso)\
        .filter(model_permiso.MenuPermiso.id_menu.in_(ids_menu))\
        .all()

    permisos_por_menu: dict[int, list] = {}
    for mp in menu_permisos:
        permisos_por_menu.setdefault(mp.id_menu, []).append(mp)

    otorgados = set(
        row.id_menu_permiso for row in
        db.query(model_permiso.RolPermiso).filter(model_permiso.RolPermiso.id_rol == id_rol).all()
    )

    resultado = []
    for f in formularios:
        acciones_menu = permisos_por_menu.get(f.id_menu, [])
        # Orden fijo Ver/Crear/Editar/Buscar/Eliminar, solo las que existan para este formulario
        acciones_ordenadas = sorted(acciones_menu, key=lambda mp: ORDEN_ACCIONES.index(mp.permiso.codigo))
        resultado.append({
            "id_menu": f.id_menu,
            "nombre": f.nombre,
            "acciones": [
                {
                    "id_menu_permiso": mp.id_menu_permiso,
                    "codigo": mp.permiso.codigo,
                    "nombre": mp.permiso.nombre,
                    "otorgado": mp.id_menu_permiso in otorgados
                }
                for mp in acciones_ordenadas
            ]
        })

    return resultado


# Todos los permisos (todas las acciones, no solo Ver) del usuario en la empresa
# activa, agrupados por codigo de formulario - usado por el guard de rutas del
# frontend (se trae una sola vez por sesion/empresa y se cachea en el cliente,
# en vez de consultar al backend en cada navegacion).
def get_mis_permisos(db: Session, id_usuario: int, id_emp: int) -> dict[str, list[str]]:
    if usuario_es_superadmin(db, id_usuario, id_emp):
        # Acceso total: todas las acciones de todos los formularios, incluidos
        # los que se agreguen en el futuro (no depende de md_rol_permiso).
        filas = db.query(Menu.codigo, model_permiso.Permiso.codigo)\
            .select_from(model_permiso.MenuPermiso)\
            .join(Menu, Menu.id_menu == model_permiso.MenuPermiso.id_menu)\
            .join(model_permiso.Permiso, model_permiso.Permiso.id_permiso == model_permiso.MenuPermiso.id_permiso)\
            .all()
        resultado_total: dict[str, list[str]] = {}
        for codigo_menu, codigo_accion in filas:
            resultado_total.setdefault(codigo_menu, []).append(codigo_accion)
        return resultado_total

    ids_rol = [
        row.id_rol for row in
        db.query(Rol.id_rol)
        .join(RolXUsuario, RolXUsuario.id_rol == Rol.id_rol)
        .filter(RolXUsuario.id_usuario == id_usuario, Rol.id_emp == id_emp, Rol.activo == True)
        .all()
    ]
    if not ids_rol:
        return {}

    filas = (
        db.query(Menu.codigo, model_permiso.Permiso.codigo)
        .select_from(model_permiso.RolPermiso)
        .join(model_permiso.MenuPermiso, model_permiso.MenuPermiso.id_menu_permiso == model_permiso.RolPermiso.id_menu_permiso)
        .join(Menu, Menu.id_menu == model_permiso.MenuPermiso.id_menu)
        .join(model_permiso.Permiso, model_permiso.Permiso.id_permiso == model_permiso.MenuPermiso.id_permiso)
        .filter(model_permiso.RolPermiso.id_rol.in_(ids_rol))
        .distinct()
        .all()
    )

    resultado: dict[str, list[str]] = {}
    for codigo_menu, codigo_accion in filas:
        resultado.setdefault(codigo_menu, []).append(codigo_accion)

    return resultado


def guardar_matriz(db: Session, id_rol: int, id_modulo: int, otorgados: list[int]):
    # Universo de id_menu_permiso que pertenecen a este modulo (lo unico que esta
    # pantalla puede tocar - no debe afectar los permisos de otros modulos).
    ids_menu_del_modulo = [
        row.id_menu for row in db.query(Menu.id_menu).filter(Menu.id_modulo == id_modulo).all()
    ]
    ids_menu_permiso_del_modulo = set(
        row.id_menu_permiso for row in
        db.query(model_permiso.MenuPermiso.id_menu_permiso)
        .filter(model_permiso.MenuPermiso.id_menu.in_(ids_menu_del_modulo)).all()
    )

    # Solo se aceptan ids que realmente pertenecen al modulo filtrado (defensivo).
    otorgados_validos = ids_menu_permiso_del_modulo.intersection(otorgados)

    db.query(model_permiso.RolPermiso).filter(
        model_permiso.RolPermiso.id_rol == id_rol,
        model_permiso.RolPermiso.id_menu_permiso.in_(ids_menu_permiso_del_modulo)
    ).delete(synchronize_session=False)
    db.flush()

    for id_menu_permiso in otorgados_validos:
        db.add(model_permiso.RolPermiso(id_rol=id_rol, id_menu_permiso=id_menu_permiso))

    db.commit()
