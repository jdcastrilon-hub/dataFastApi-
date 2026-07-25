from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from . import model_menu, schema_menu
from app.modules.core.roles.model_rol import Rol, RolXUsuario
from app.modules.core.roles.repository_rol import usuario_es_superadmin
from app.modules.core.permisos.model_permiso import RolPermiso, MenuPermiso, Permiso


# ids de md_menu que el usuario puede VER, segun los roles que tenga en la
# empresa activa (deny-by-default: si no tiene ningun rol con el permiso VER
# otorgado sobre un formulario, ese formulario no aparece).
def _ids_menu_visibles(db: Session, id_usuario: int, id_emp: int) -> set[int]:
    ids_rol = [
        row.id_rol for row in
        db.query(Rol.id_rol)
        .join(RolXUsuario, RolXUsuario.id_rol == Rol.id_rol)
        .filter(RolXUsuario.id_usuario == id_usuario, Rol.id_emp == id_emp, Rol.activo == True)
        .all()
    ]
    if not ids_rol:
        return set()

    filas = (
        db.query(MenuPermiso.id_menu)
        .join(RolPermiso, RolPermiso.id_menu_permiso == MenuPermiso.id_menu_permiso)
        .join(Permiso, Permiso.id_permiso == MenuPermiso.id_permiso)
        .filter(RolPermiso.id_rol.in_(ids_rol), Permiso.codigo == 'VER')
        .distinct()
        .all()
    )
    return set(row.id_menu for row in filas)


def obtener_menu(db: Session, id_usuario: int, id_emp: int):

    registros = (
        db.query(model_menu.Menu)
        .filter(model_menu.Menu.activo == True, model_menu.Menu.visible == True)
        .order_by(model_menu.Menu.orden)
        .all()
    )

    # Superadmin: acceso total, ni siquiera pasa por md_rol_permiso (incluye
    # formularios futuros sin necesidad de otorgarselos explicitamente).
    if usuario_es_superadmin(db, id_usuario, id_emp):
        ids_con_ver = set(item.id_menu for item in registros)
    else:
        ids_con_ver = _ids_menu_visibles(db, id_usuario, id_emp)

    hijos_por_padre: dict = {}
    for item in registros:
        hijos_por_padre.setdefault(item.id_padre, []).append(item)

    visibles: set = set()

    # Un formulario "hoja" (tiene ruta propia) es visible si tiene VER otorgado.
    # Un contenedor (Maestros/Transacciones/raiz de modulo, sin ruta) es visible
    # si al menos uno de sus hijos es visible - de lo contrario seria una carpeta
    # vacia que no lleva a ningun lado.
    def es_visible(item) -> bool:
        if item.id_menu in visibles:
            return True
        if item.ruta:
            resultado = item.id_menu in ids_con_ver
        else:
            hijos = hijos_por_padre.get(item.id_menu, [])
            resultado = any(es_visible(h) for h in hijos)
        if resultado:
            visibles.add(item.id_menu)
        return resultado

    for item in registros:
        es_visible(item)

    registros_visibles = [item for item in registros if item.id_menu in visibles]

    # Convertir cada registro del ORM a MenuResponse
    menus = {}
    for item in registros_visibles:
        menu = schema_menu.MenuResponse.model_validate(item)
        menus[menu.id_menu] = menu

    arbol = []

    # Construir el árbol
    for item in registros_visibles:

        menu = menus[item.id_menu]

        if item.id_padre is None:
            arbol.append(menu)
        else:
            padre = menus.get(item.id_padre)

            if padre:
                padre.children.append(menu)

    return arbol
