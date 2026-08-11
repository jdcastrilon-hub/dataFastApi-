"""s_costovariacion tabla y triggers, backfill desde p_costos

Tabla derivada (s_, mismo criterio operativo que s_stkbodegas: la app nunca
le escribe directo, la mantiene un trigger reaccionando a p_costos) con una
fila por CADA evento donde el costo promedio realmente cambio
(imp_costo_unitario != imp_costo_actual). Reemplaza la idea de filtrar
p_costos por fecha en el kardex - esta tabla ya viene pre-filtrada a solo
cambios reales, sin importar cuantas filas (ventas, etc.) tenga p_costos.

Se mantiene con un par de triggers (AFTER INSERT / BEFORE DELETE en p_costos,
mismo patron que ins_p_costos/del_p_costos ya existentes) en vez de tocar
sp_compradirecta/sp_ajustecostos/sp_compras_devoluciones - asi cualquier
escritor futuro de p_costos (o el ya existente CargaStock) queda cubierto
automaticamente sin tener que acordarse de agregarle el insert a mano.

Revision ID: ad0ac75b0914
Revises: b0c94e1907b5
Create Date: 2026-08-05 19:17:46.451350

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ad0ac75b0914'
down_revision: Union[str, Sequence[str], None] = 'b0c94e1907b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TABLE public.s_costovariacion (
            id_trans integer NOT NULL,
            linea integer NOT NULL,
            id_emp integer NOT NULL,
            id_bodega integer NOT NULL,
            id_articulo integer NOT NULL,
            id_proveedor integer,
            fec_doc date NOT NULL,
            documento character varying NOT NULL,
            nro_docum integer,
            vista character varying,
            cantidad integer,
            costo_anterior numeric NOT NULL,
            costo_movimiento numeric NOT NULL,
            costo_nuevo_promedio numeric NOT NULL,
            usuario_mod character varying(50),
            fecha_mod timestamp without time zone NOT NULL DEFAULT now(),
            PRIMARY KEY (id_trans, linea)
        )
    """)

    # Backfill: todo lo que ya esta en p_costos y representa un cambio real
    # (p_costos.usuario_mod solo existe desde la migracion 8f002b62bd05, por
    # eso las filas historicas de antes de esa fecha quedan con usuario null).
    op.execute("""
        INSERT INTO public.s_costovariacion (
            id_trans, linea, id_emp, id_bodega, id_articulo, id_proveedor, fec_doc,
            documento, nro_docum, vista, cantidad, costo_anterior, costo_movimiento,
            costo_nuevo_promedio, usuario_mod, fecha_mod)
        SELECT
            id_trans, linea, id_emp, id_bodega, id_articulo, NULLIF(id_proveedor, 0), fec_doc,
            documento, nro_docum, vista, cantidad, imp_costo_actual, imp_costo_nuevo,
            imp_costo_unitario, usuario_mod, fecha_mod
        FROM public.p_costos
        WHERE imp_costo_unitario IS DISTINCT FROM imp_costo_actual
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.p_costos_variacion_insert()
         RETURNS trigger
         LANGUAGE plpgsql
        AS $function$
        BEGIN
            IF NEW.imp_costo_unitario IS DISTINCT FROM NEW.imp_costo_actual THEN
                INSERT INTO public.s_costovariacion (
                    id_trans, linea, id_emp, id_bodega, id_articulo, id_proveedor, fec_doc,
                    documento, nro_docum, vista, cantidad, costo_anterior, costo_movimiento,
                    costo_nuevo_promedio, usuario_mod, fecha_mod)
                VALUES (
                    NEW.id_trans, NEW.linea, NEW.id_emp, NEW.id_bodega, NEW.id_articulo,
                    NULLIF(NEW.id_proveedor, 0), NEW.fec_doc, NEW.documento, NEW.nro_docum,
                    NEW.vista, NEW.cantidad, NEW.imp_costo_actual, NEW.imp_costo_nuevo,
                    NEW.imp_costo_unitario, NEW.usuario_mod, NEW.fecha_mod)
                ON CONFLICT (id_trans, linea) DO UPDATE SET
                    id_emp = EXCLUDED.id_emp, id_bodega = EXCLUDED.id_bodega,
                    id_articulo = EXCLUDED.id_articulo, id_proveedor = EXCLUDED.id_proveedor,
                    fec_doc = EXCLUDED.fec_doc, documento = EXCLUDED.documento,
                    nro_docum = EXCLUDED.nro_docum, vista = EXCLUDED.vista,
                    cantidad = EXCLUDED.cantidad, costo_anterior = EXCLUDED.costo_anterior,
                    costo_movimiento = EXCLUDED.costo_movimiento,
                    costo_nuevo_promedio = EXCLUDED.costo_nuevo_promedio,
                    usuario_mod = EXCLUDED.usuario_mod, fecha_mod = EXCLUDED.fecha_mod;
            END IF;
            RETURN NEW;
        END;
        $function$;
    """)

    op.execute("""
        CREATE TRIGGER ins_p_costos_variacion AFTER INSERT ON public.p_costos
        FOR EACH ROW EXECUTE FUNCTION public.p_costos_variacion_insert()
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION public.p_costos_variacion_delete()
         RETURNS trigger
         LANGUAGE plpgsql
        AS $function$
        BEGIN
            DELETE FROM public.s_costovariacion WHERE id_trans = OLD.id_trans AND linea = OLD.linea;
            RETURN OLD;
        END;
        $function$;
    """)

    op.execute("""
        CREATE TRIGGER del_p_costos_variacion BEFORE DELETE ON public.p_costos
        FOR EACH ROW EXECUTE FUNCTION public.p_costos_variacion_delete()
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS del_p_costos_variacion ON public.p_costos")
    op.execute("DROP FUNCTION IF EXISTS public.p_costos_variacion_delete()")
    op.execute("DROP TRIGGER IF EXISTS ins_p_costos_variacion ON public.p_costos")
    op.execute("DROP FUNCTION IF EXISTS public.p_costos_variacion_insert()")
    op.execute("DROP TABLE IF EXISTS public.s_costovariacion")
