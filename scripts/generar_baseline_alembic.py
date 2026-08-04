"""
Genera el DDL completo del esquema actual (secuencias + tablas + funciones +
triggers) leyendo directamente la base de datos en vivo, sin depender de
pg_dump/psql (no estan instalados en este entorno).

Se uso para armar la migracion baseline de Alembic (ver alembic/versions/) que
describe el estado del esquema el dia que se adopto Alembic. Se deja como
utilidad reusable: si en el futuro hay sospecha de "drift" entre lo que dicen
los modelos SQLAlchemy y lo que realmente existe en la BD, este script vuelve
a mostrar el estado real tal cual esta en Postgres.

Nota importante descubierta al construir esto: la reflection por defecto de
SQLAlchemy "simplifica" cualquier columna entera con default nextval() a
SERIAL/BIGSERIAL, inventando un nombre de secuencia nuevo (`tabla_columna_seq`)
y DESCARTANDO el nombre/relacion real. Esto rompe dos casos reales de este
esquema: `id_transaccion` es una secuencia COMPARTIDA entre 8 tablas (un
contador transaccional unico cruzando ajustestock/compras/traslados/etc), y
`md_empresas.id_emp` usa la secuencia con nombre legado `m_empresa_id_emp_seq`
(de antes de que la tabla se renombrara). Por eso este script fuerza el
default literal exacto de information_schema en vez de dejar que SQLAlchemy
lo re-invente.

No escribe nada - es de solo lectura. Imprime el DDL a stdout.

Uso:
    python scripts/generar_baseline_alembic.py > archivo.sql
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import DefaultClause, MetaData, text
from sqlalchemy.schema import CreateTable

from app.database import engine


def obtener_defaults_reales() -> dict[tuple[str, str], str]:
    """Default real (texto exacto de information_schema) de cada columna con
    nextval(), sin la simplificacion a SERIAL que hace la reflection normal."""
    with engine.connect() as conn:
        filas = conn.execute(text("""
            SELECT table_name, column_name, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND column_default LIKE 'nextval(%'
        """)).fetchall()
    return {(f.table_name, f.column_name): f.column_default for f in filas}


def generar_ddl_secuencias() -> str:
    """TODAS las secuencias del esquema, creadas antes que las tablas. Como
    se fuerza el default literal en cada columna (ver mas abajo), ninguna
    tabla vuelve a crear una secuencia via SERIAL - así que no hay riesgo de
    'ya existe' al pre-crearlas todas aqui."""
    with engine.connect() as conn:
        nombres = [r[0] for r in conn.execute(text(
            "SELECT sequencename FROM pg_sequences WHERE schemaname='public' ORDER BY sequencename"
        )).fetchall()]
    return "\n".join(f'CREATE SEQUENCE IF NOT EXISTS public."{n}";' for n in nombres)


def generar_ddl_tablas(defaults_reales: dict[tuple[str, str], str]) -> str:
    """Reflecta TODAS las tablas del esquema public (tengan o no modelo
    SQLAlchemy) y genera su CREATE TABLE, en el orden correcto segun sus
    dependencias de foreign key. Para columnas con secuencia, se fuerza el
    default literal real en vez de dejar que SQLAlchemy renderice SERIAL."""
    metadata = MetaData()
    metadata.reflect(bind=engine, schema="public")

    for tabla in metadata.sorted_tables:
        for columna in tabla.columns:
            clave = (tabla.name, columna.name)
            if clave in defaults_reales:
                columna.autoincrement = False
                columna.server_default = DefaultClause(text(defaults_reales[clave]))

    partes = []
    for tabla in metadata.sorted_tables:
        ddl = str(CreateTable(tabla).compile(engine)).strip()
        partes.append(ddl + ";")
    return "\n\n".join(partes)


def generar_ddl_ownership_secuencias() -> str:
    """Para las secuencias que SI son propiedad exclusiva de una columna
    (dependencia 'a' en pg_depend - lo que Postgres considera un SERIAL de
    verdad), se restaura esa relacion con ALTER SEQUENCE ... OWNED BY. Las
    que no tienen esa relacion en el esquema real (ej. id_transaccion,
    compartida entre 8 tablas) se dejan independientes a proposito - asi
    era en el esquema original."""
    with engine.connect() as conn:
        filas = conn.execute(text("""
            SELECT s.relname AS secuencia, t.relname AS tabla, a.attname AS columna
            FROM pg_depend d
            JOIN pg_class s ON d.objid = s.oid
            JOIN pg_class t ON d.refobjid = t.oid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
            JOIN pg_namespace n ON s.relnamespace = n.oid
            WHERE d.deptype = 'a' AND s.relkind = 'S' AND n.nspname = 'public'
            ORDER BY s.relname
        """)).fetchall()
    return "\n".join(
        f'ALTER SEQUENCE public."{f.secuencia}" OWNED BY public."{f.tabla}"."{f.columna}";'
        for f in filas
    )


def generar_ddl_funciones() -> str:
    """Todas las funciones/stored procedures del esquema public, via
    pg_get_functiondef (equivalente a lo que haria pg_dump, sin necesitarlo)."""
    with engine.connect() as conn:
        filas = conn.execute(text("""
            SELECT pg_get_functiondef(p.oid) AS definicion
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'public'
            ORDER BY p.proname
        """)).fetchall()
    return "\n\n".join(f"{fila.definicion};" for fila in filas)


def generar_ddl_triggers() -> str:
    """Todos los triggers del esquema public, via pg_get_triggerdef."""
    with engine.connect() as conn:
        filas = conn.execute(text("""
            SELECT pg_get_triggerdef(t.oid) AS definicion
            FROM pg_trigger t
            JOIN pg_class c ON t.tgrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE n.nspname = 'public' AND NOT t.tgisinternal
            ORDER BY c.relname, t.tgname
        """)).fetchall()
    return "\n\n".join(f"{fila.definicion};" for fila in filas)


def main() -> None:
    # En Windows, stdout redirigido a archivo NO usa UTF-8 por defecto (usa el
    # codepage de la consola) - varias funciones/comentarios tienen tildes, lo
    # que corrompia el archivo generado. Se fuerza UTF-8 explicitamente.
    sys.stdout.reconfigure(encoding="utf-8")

    print("-- ============ DEFAULTS REALES ============", file=sys.stderr)
    defaults_reales = obtener_defaults_reales()
    print("-- ============ SECUENCIAS ============", file=sys.stderr)
    ddl_secuencias = generar_ddl_secuencias()
    print("-- ============ TABLAS ============", file=sys.stderr)
    ddl_tablas = generar_ddl_tablas(defaults_reales)
    print("-- ============ OWNERSHIP DE SECUENCIAS ============", file=sys.stderr)
    ddl_ownership = generar_ddl_ownership_secuencias()
    print("-- ============ FUNCIONES ============", file=sys.stderr)
    ddl_funciones = generar_ddl_funciones()
    print("-- ============ TRIGGERS ============", file=sys.stderr)
    ddl_triggers = generar_ddl_triggers()

    print("-- SECUENCIAS")
    print(ddl_secuencias)
    print()
    print("-- TABLAS")
    print(ddl_tablas)
    print()
    print("-- OWNERSHIP DE SECUENCIAS (solo las que son de una sola columna)")
    print(ddl_ownership)
    print()
    print("-- FUNCIONES")
    print(ddl_funciones)
    print()
    print("-- TRIGGERS")
    print(ddl_triggers)


if __name__ == "__main__":
    main()
