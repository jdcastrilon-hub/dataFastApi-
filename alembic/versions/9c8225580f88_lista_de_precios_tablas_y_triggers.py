"""lista de precios: tablas y triggers

Crea el motor de lista de precios: catalogo de listas (base y de cliente en
una sola tabla), el ledger p_precios + snapshot s_precioxarticulo (mismo
patron que p_costos/s_costoxbodegas, incluyendo la ausencia deliberada de FKs
en esas dos - referencia polimorfica, ver docs/tecnica/base-de-datos.md),
permisos de lista por usuario, y reglas de descuento por categoria ancladas a
la lista general de cada empresa.

Solo tablas/triggers - backend y frontend se implementan aparte.

Revision ID: 9c8225580f88
Revises: 973534e551a9
Create Date: 2026-07-28 20:58:52.427301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c8225580f88'
down_revision: Union[str, Sequence[str], None] = '973534e551a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- m_listaprecio: catalogo de listas (base y de cliente en una sola tabla) ---
    op.execute("""
        CREATE TABLE public.m_listaprecio (
            id_lista SERIAL PRIMARY KEY,
            id_emp INTEGER NOT NULL REFERENCES public.md_empresas(id_emp),
            nombre VARCHAR(50) NOT NULL,
            -- NULL = lista base (General/Mayorista); con valor = lista de ese
            -- cliente puntual. Es la unica fuente de verdad del tipo de lista,
            -- sin un booleano aparte que pueda quedar inconsistente.
            id_cliente INTEGER NULL REFERENCES public.m_clientes(id_cliente),
            -- Marca la lista "general" de la empresa: es la que ancla las
            -- reglas de descuento por categoria (ver m_reglaprecio) y la que
            -- usan los triggers para saber contra que precio calcular.
            es_general BOOLEAN NOT NULL DEFAULT false,
            activo BOOLEAN NOT NULL DEFAULT true,
            fecha_mod TIMESTAMP NOT NULL DEFAULT now()
        );
    """)

    # Una sola lista general activa por empresa - es el ancla de las reglas
    # de categoria, no puede haber ambiguedad sobre cual es.
    op.execute("""
        CREATE UNIQUE INDEX ux_listaprecio_general_por_emp
            ON public.m_listaprecio (id_emp)
            WHERE es_general = true AND activo = true;
    """)

    # --- p_precios: ledger, mismo patron que p_costos (sin FKs, referencia
    # polimorfica intencional; clave (id_trans, id_articulo, linea) igual que
    # p_costos, no un id propio) ---
    op.execute("""
        CREATE TABLE public.p_precios (
            id_trans INTEGER NOT NULL,
            linea INTEGER NOT NULL,
            id_emp INTEGER NOT NULL,
            id_lista INTEGER NOT NULL,
            id_articulo INTEGER NOT NULL,
            precio_anterior NUMERIC(20,2) NULL,
            precio_nuevo NUMERIC(20,2) NOT NULL,
            -- Quien/que origino esta fila: CARGA_ITEMS | REGLA_CATEGORIA | MANUAL
            origen VARCHAR(20) NOT NULL,
            usuario_mod VARCHAR(50) NULL,
            fecha_mod TIMESTAMP NOT NULL DEFAULT now(),
            PRIMARY KEY (id_trans, id_articulo, linea)
        );
    """)

    op.execute("""
        CREATE INDEX ix_precios_lista_articulo
            ON public.p_precios (id_lista, id_articulo);
    """)

    # --- s_precioxarticulo: snapshot vigente, mismo patron que s_costoxbodegas
    # (sin FKs) ---
    op.execute("""
        CREATE TABLE public.s_precioxarticulo (
            id_lista INTEGER NOT NULL,
            id_articulo INTEGER NOT NULL,
            id_emp INTEGER NOT NULL,
            precio_venta NUMERIC(20,2) NOT NULL,
            fecha_mod TIMESTAMP NOT NULL DEFAULT now(),
            PRIMARY KEY (id_lista, id_articulo)
        );
    """)

    # --- m_listaprecioxuser: permiso por usuario, solo relevante para listas
    # base (id_cliente IS NULL) - la lista general no necesita fila aqui
    # (acceso implicito), y las listas de cliente nunca usan esta tabla. ---
    op.execute("""
        CREATE TABLE public.m_listaprecioxuser (
            id_usuario INTEGER NOT NULL REFERENCES public.md_usuarios(id_usuario),
            id_lista INTEGER NOT NULL REFERENCES public.m_listaprecio(id_lista),
            PRIMARY KEY (id_usuario, id_lista)
        );
    """)

    # --- m_reglaprecio: regla de descuento por categoria/subcategoria sobre
    # la lista general, atada a una lista de cliente destino. Es una regla
    # viva (no un calculo unico) - los triggers de abajo la mantienen
    # sincronizada cuando cambia el precio general o se agregan articulos
    # nuevos a la categoria. ---
    op.execute("""
        CREATE TABLE public.m_reglaprecio (
            id_regla SERIAL PRIMARY KEY,
            id_emp INTEGER NOT NULL REFERENCES public.md_empresas(id_emp),
            id_lista INTEGER NOT NULL REFERENCES public.m_listaprecio(id_lista),
            id_categoria INTEGER NULL REFERENCES public.m_categorias(id),
            id_subcategoria INTEGER NULL REFERENCES public.m_subcategorias(id),
            porcentaje NUMERIC(5,2) NOT NULL,
            activo BOOLEAN NOT NULL DEFAULT true,
            fecha_mod TIMESTAMP NOT NULL DEFAULT now(),
            CONSTRAINT ck_reglaprecio_una_categoria CHECK (
                (id_categoria IS NOT NULL AND id_subcategoria IS NULL) OR
                (id_categoria IS NULL AND id_subcategoria IS NOT NULL)
            )
        );
    """)

    # --- Trigger 1: mantiene el snapshot vigente. Reemplazo puro, SIN ningun
    # calculo (a diferencia de s_costoxbodegas, que promedia contra la
    # cantidad existente) - "ultimo valor gana". ---
    op.execute("""
        CREATE OR REPLACE FUNCTION public.p_precios_insert()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            INSERT INTO public.s_precioxarticulo (id_lista, id_articulo, id_emp, precio_venta, fecha_mod)
            VALUES (NEW.id_lista, NEW.id_articulo, NEW.id_emp, NEW.precio_nuevo, NEW.fecha_mod)
            ON CONFLICT (id_lista, id_articulo)
            DO UPDATE SET
                precio_venta = EXCLUDED.precio_venta,
                fecha_mod = EXCLUDED.fecha_mod;

            RETURN NEW;
        END;
        $function$;
    """)

    op.execute("""
        CREATE TRIGGER ins_p_precios
        AFTER INSERT ON public.p_precios
        FOR EACH ROW EXECUTE FUNCTION public.p_precios_insert();
    """)

    # --- Trigger 2: cuando el precio que acaba de entrar es el de la lista
    # GENERAL de la empresa, revisa si hay reglas de categoria activas que
    # apliquen a ese articulo y les genera su propia fila en p_precios
    # (que a su vez dispara el trigger 1 para esa lista de cliente). ---
    op.execute("""
        CREATE OR REPLACE FUNCTION public.p_precios_aplicar_reglas()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        DECLARE
            v_es_general BOOLEAN;
            v_id_categoria INTEGER;
            v_id_subcategoria INTEGER;
            v_regla RECORD;
            v_id_trans INTEGER;
        BEGIN
            SELECT es_general INTO v_es_general
            FROM public.m_listaprecio
            WHERE id_lista = NEW.id_lista;

            IF NOT COALESCE(v_es_general, false) THEN
                RETURN NEW;
            END IF;

            SELECT id_categoria, id_subcategoria INTO v_id_categoria, v_id_subcategoria
            FROM public.m_articulos
            WHERE id_articulo = NEW.id_articulo;

            FOR v_regla IN
                SELECT id_lista, porcentaje
                FROM public.m_reglaprecio
                WHERE activo = true
                  AND id_emp = NEW.id_emp
                  AND (id_categoria = v_id_categoria OR id_subcategoria = v_id_subcategoria)
            LOOP
                v_id_trans := nextval('id_transaccion');

                INSERT INTO public.p_precios (
                    id_trans, linea, id_emp, id_lista, id_articulo,
                    precio_anterior, precio_nuevo, origen, usuario_mod, fecha_mod
                )
                VALUES (
                    v_id_trans, 1, NEW.id_emp, v_regla.id_lista, NEW.id_articulo,
                    (SELECT precio_venta FROM public.s_precioxarticulo
                        WHERE id_lista = v_regla.id_lista AND id_articulo = NEW.id_articulo),
                    ROUND(NEW.precio_nuevo * (1 - v_regla.porcentaje / 100.0), 2),
                    'REGLA_CATEGORIA', 'sistema', now()
                );
            END LOOP;

            RETURN NEW;
        END;
        $function$;
    """)

    op.execute("""
        CREATE TRIGGER ins_p_precios_reglas
        AFTER INSERT ON public.p_precios
        FOR EACH ROW EXECUTE FUNCTION public.p_precios_aplicar_reglas();
    """)

    # --- Trigger 3: al crear/editar una regla (o reactivarla), recalcula de
    # una vez contra los articulos que YA tienen precio general hoy - el
    # trigger 2 por si solo solo reacciona a cambios futuros. Si la regla
    # queda inactiva, no se tocan los precios ya generados. ---
    op.execute("""
        CREATE OR REPLACE FUNCTION public.m_reglaprecio_recalcular()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $function$
        DECLARE
            v_id_trans INTEGER;
            v_linea INTEGER := 0;
            v_fila RECORD;
        BEGIN
            IF NOT NEW.activo THEN
                RETURN NEW;
            END IF;

            v_id_trans := nextval('id_transaccion');

            FOR v_fila IN
                SELECT s.id_articulo, s.precio_venta
                FROM public.s_precioxarticulo s
                INNER JOIN public.m_listaprecio l
                    ON l.id_lista = s.id_lista AND l.es_general = true AND l.id_emp = NEW.id_emp
                INNER JOIN public.m_articulos a ON a.id_articulo = s.id_articulo
                WHERE (NEW.id_categoria IS NOT NULL AND a.id_categoria = NEW.id_categoria)
                   OR (NEW.id_subcategoria IS NOT NULL AND a.id_subcategoria = NEW.id_subcategoria)
            LOOP
                v_linea := v_linea + 1;

                INSERT INTO public.p_precios (
                    id_trans, linea, id_emp, id_lista, id_articulo,
                    precio_anterior, precio_nuevo, origen, usuario_mod, fecha_mod
                )
                VALUES (
                    v_id_trans, v_linea, NEW.id_emp, NEW.id_lista, v_fila.id_articulo,
                    (SELECT precio_venta FROM public.s_precioxarticulo
                        WHERE id_lista = NEW.id_lista AND id_articulo = v_fila.id_articulo),
                    ROUND(v_fila.precio_venta * (1 - NEW.porcentaje / 100.0), 2),
                    'REGLA_CATEGORIA', 'sistema', now()
                );
            END LOOP;

            RETURN NEW;
        END;
        $function$;
    """)

    op.execute("""
        CREATE TRIGGER trg_m_reglaprecio_recalcular
        AFTER INSERT OR UPDATE OF porcentaje, activo ON public.m_reglaprecio
        FOR EACH ROW EXECUTE FUNCTION public.m_reglaprecio_recalcular();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_m_reglaprecio_recalcular ON public.m_reglaprecio;")
    op.execute("DROP FUNCTION IF EXISTS public.m_reglaprecio_recalcular();")
    op.execute("DROP TRIGGER IF EXISTS ins_p_precios_reglas ON public.p_precios;")
    op.execute("DROP FUNCTION IF EXISTS public.p_precios_aplicar_reglas();")
    op.execute("DROP TRIGGER IF EXISTS ins_p_precios ON public.p_precios;")
    op.execute("DROP FUNCTION IF EXISTS public.p_precios_insert();")

    op.execute("DROP TABLE IF EXISTS public.m_reglaprecio;")
    op.execute("DROP TABLE IF EXISTS public.m_listaprecioxuser;")
    op.execute("DROP TABLE IF EXISTS public.s_precioxarticulo;")
    op.execute("DROP TABLE IF EXISTS public.p_precios;")
    op.execute("DROP TABLE IF EXISTS public.m_listaprecio;")
