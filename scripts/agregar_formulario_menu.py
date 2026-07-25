"""
Agrega una hoja nueva al arbol de menu (md_menu) y sus acciones disponibles
(md_menu_permisos) en una sola transaccion.

Antes de este script, cada formulario nuevo requeria dos inserts manuales por
separado (uno en md_menu, otro en md_menu_permisos) y era facil olvidar el
segundo - sobre todo porque md_menu_permisos no existia hasta que se construyo
la matriz de permisos (ver Roles > Permisos en Administracion). Este script deja
ambos coordinados y documentados en un solo comando.

Ejemplos:

    # Formulario visible en el sidebar (caso normal: un master/transaccional nuevo)
    python scripts/agregar_formulario_menu.py \
        --codigo INV_LOTES --nombre "Lotes" --id-modulo 1 --id-padre 2 \
        --ruta /lotes/new --orden 7

    # Formulario "invisible" (vive dentro de un tab de otra pantalla, como las
    # pestanas de Administracion: no debe aparecer como hijo en el sidebar, pero
    # si necesita sus propias acciones para la matriz de permisos)
    python scripts/agregar_formulario_menu.py \
        --codigo ADM_USR --nombre "Usuarios" --id-modulo 5 --id-padre 51 \
        --ruta /administracion/usuarios --visible false

    # Reporte/monitor (solo Ver+Buscar, sin Crear/Editar/Eliminar)
    python scripts/agregar_formulario_menu.py \
        --codigo INV_MON2 --nombre "Monitor Costos" --id-modulo 1 --id-padre 1 \
        --ruta /monitorcostos --icono monitor --acciones VER,BUSCAR
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from app.database import SQLALCHEMY_DATABASE_URL

ACCIONES_POR_DEFECTO = ['VER', 'CREAR', 'EDITAR', 'BUSCAR', 'ELIMINAR']


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--codigo', required=True, help='Codigo unico del menu, ej. INV_LOTES')
    parser.add_argument('--nombre', required=True, help='Nombre a mostrar')
    parser.add_argument('--id-modulo', required=True, type=int, help='id_modulo (1=INV,2=COM,3=VEN,4=TES,5=ADM)')
    parser.add_argument('--id-padre', type=int, default=None, help='id_menu del contenedor padre (omitir si es raiz)')
    parser.add_argument('--ruta', required=True, help='Ruta Angular (o pseudo-ruta si --visible=false)')
    parser.add_argument('--icono', default=None, help='Nombre del icono Material (opcional)')
    parser.add_argument('--orden', type=int, default=99, help='Orden dentro de su nivel (default 99)')
    parser.add_argument('--visible', type=str, default='true', choices=['true', 'false'],
                         help="'false' para formularios que no deben aparecer como item propio en el sidebar "
                              "(ej. una pestana dentro de otra pantalla) pero si necesitan permisos propios")
    parser.add_argument('--acciones', default=','.join(ACCIONES_POR_DEFECTO),
                         help="Lista separada por comas de codigos de md_permisos a habilitar para este formulario "
                              "(default: las 5). Ej. 'VER,BUSCAR' para un reporte de solo lectura.")
    return parser.parse_args()


def main():
    args = parse_args()
    visible = args.visible == 'true'
    acciones = [a.strip().upper() for a in args.acciones.split(',') if a.strip()]

    conn = psycopg2.connect(SQLALCHEMY_DATABASE_URL)
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO md_menu (id_modulo, codigo, nombre, ruta, icono, id_padre, orden, visible, activo, es_contenedor)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, true, false)
            RETURNING id_menu
            """,
            (args.id_modulo, args.codigo, args.nombre, args.ruta, args.icono, args.id_padre, args.orden, visible)
        )
        id_menu = cur.fetchone()[0]

        cur.execute("SELECT id_permiso, codigo FROM md_permisos WHERE codigo = ANY(%s)", (acciones,))
        encontrados = dict(cur.fetchall())
        faltantes = set(acciones) - set(encontrados.values())
        if faltantes:
            raise ValueError(f"Codigos de accion desconocidos en md_permisos: {faltantes}")

        for id_permiso in encontrados:
            cur.execute(
                "INSERT INTO md_menu_permisos (id_menu, id_permiso) VALUES (%s, %s)",
                (id_menu, id_permiso)
            )

        conn.commit()
        print(f"OK: md_menu.id_menu={id_menu} ('{args.nombre}'), "
              f"{len(encontrados)} acciones en md_menu_permisos ({', '.join(sorted(encontrados.values()))}), "
              f"visible={visible}")
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    main()
