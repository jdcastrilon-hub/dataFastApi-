from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload
from . import model_menu, schema_menu
from app.modules.core.roles.model_rol import Rol, RolXUsuario
from app.modules.core.roles.repository_rol import usuario_es_superadmin
from app.modules.core.permisos.model_permiso import RolPermiso, MenuPermiso, Permiso
from app.modules.core.permisos.repository_permiso import _ids_modulo_deshabilitados


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

    # Modulos deshabilitados para la empresa activa quedan fuera del universo
    # completo ANTES de mirar rol/superadmin - ni el propio superadmin de la
    # empresa ve un modulo que su empresa tiene apagado (ver
    # docs/tecnica/specs/core/delegacion-permisos-menu-exclusivo.md, Pieza 1).
    ids_modulo_deshabilitados = _ids_modulo_deshabilitados(db, id_emp)
    if ids_modulo_deshabilitados:
        registros = [r for r in registros if r.id_modulo not in ids_modulo_deshabilitados]

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


# Registra una hoja nueva en md_menu y sus acciones en md_menu_permisos, en una
# sola transaccion (mismo trabajo que scripts/agregar_formulario_menu.py, ahora
# vía API - endpoint protegido a nivel de plataforma, ver controller_menu.py).
def agregar_formulario_menu(db: Session, obj: schema_menu.AgregarFormularioRequest):
    acciones = [a.strip().upper() for a in obj.acciones if a.strip()]

    encontrados = {
        row.codigo: row.id_permiso
        for row in db.query(Permiso).filter(Permiso.codigo.in_(acciones)).all()
    }
    faltantes = set(acciones) - set(encontrados.keys())
    if faltantes:
        raise HTTPException(status_code=400, detail=f"Codigos de accion desconocidos en md_permisos: {sorted(faltantes)}")

    db_menu = model_menu.Menu(
        id_modulo=obj.id_modulo,
        codigo=obj.codigo,
        nombre=obj.nombre,
        ruta=obj.ruta,
        icono=obj.icono,
        id_padre=obj.id_padre,
        orden=obj.orden,
        visible=obj.visible,
        activo=True,
        es_contenedor=False
    )
    db.add(db_menu)
    db.flush()

    for id_permiso in encontrados.values():
        db.add(MenuPermiso(id_menu=db_menu.id_menu, id_permiso=id_permiso))

    db.commit()
    db.refresh(db_menu)

    return {
        "id_menu": db_menu.id_menu,
        "codigo": db_menu.codigo,
        "nombre": db_menu.nombre,
        "acciones": sorted(encontrados.keys()),
        "visible": db_menu.visible
    }
