from sqlalchemy import desc
from sqlalchemy.orm import Session , joinedload
from . import model_menu , schema_menu

# Obtener todas las bodegas ordenadas de mayor a menor
def obtener_menu(db: Session):

        registros = (
            db.query(model_menu.Menu)
            .filter(model_menu.Menu.activo == True)
            .order_by(model_menu.Menu.orden)
            .all()
        )

        # Diccionario para acceder rápidamente por id_menu
        menus = {}

        # Convertir cada registro del ORM a MenuResponse
        for item in registros:
            menu = schema_menu.MenuResponse.model_validate(item)
            menus[menu.id_menu] = menu

        arbol = []

        # Construir el árbol
        for item in registros:

            menu = menus[item.id_menu]

            if item.id_padre is None:
                arbol.append(menu)
            else:
                padre = menus.get(item.id_padre)

                if padre:
                    padre.children.append(menu)

        return arbol
