"""m_motivoajuste cambiar activo de varchar a boolean

Mismo tratamiento que m_bodegas.activo (migracion 833750948175): unifica el
tipo de "activo" con el resto de catalogos (m_estados, m_sucursales,
m_negocios ya son boolean). sp_core_nuevaempresa inserta los 2 motivos de
ajuste por defecto con el literal 'S' - se corrige a 'true' en el mismo
CREATE OR REPLACE, o el ALTER COLUMN rompe la proxima vez que se cree una
empresa (INSERT de un boolean invalido). No se encontraron triggers ni
indices sobre m_motivoajuste.activo (a diferencia del caso de bodegas, ver
migracion bfe7e402d83f) - se audito pg_indexes/pg_trigger/pg_proc antes de
este cambio.

Revision ID: 62ad1ce865e7
Revises: c66f2b5c1d93
Create Date: 2026-08-07 10:12:54.769342

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62ad1ce865e7'
down_revision: Union[str, Sequence[str], None] = 'c66f2b5c1d93'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TABLE public.m_motivoajuste ALTER COLUMN activo TYPE boolean USING (activo = 'S');")
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_core_nuevaempresa(IN p_id_emp integer)
         LANGUAGE plpgsql
        AS $procedure$
        DECLARE
            v_logs json;
        BEGIN
            -- Logs de la empresa recien creada (misma transaccion) - se reusa tal
            -- cual en todos los maestros de abajo para no perder quien la creo.
            SELECT logs INTO v_logs FROM public.md_empresas WHERE id_emp = p_id_emp;

            -- Sucursal principal
            INSERT INTO public.m_sucursales (id_emp, cod_sucursal, nom_sucursal, id_ciudad, direccion, telefono, activo, logs, fecha_mod)
            SELECT id_emp, '01', 'Sucursal Principal', cod_ciudad, direccion, telefono, true, v_logs, now()
            FROM public.md_empresas
            WHERE id_emp = p_id_emp;

            -- Negocio principal
            INSERT INTO public.m_negocios (id_emp, cod_negocio, nom_negocio, logs, fecha_mod, activo)
            SELECT id_emp, '01', nom_emp, v_logs, now(), true
            FROM public.md_empresas
            WHERE id_emp = p_id_emp;

            -- Estados de stock por defecto
            INSERT INTO public.m_estados (id_emp, cod_estado, nom_estado, activo, obervacion, fecha_mod, logs)
            VALUES
                (p_id_emp, 'Disponible', 'Disponible en Bodega', true, 'Estado disponible para venta/consumo', now(), v_logs);

            -- Unidad de medida por defecto
            INSERT INTO public.m_unidades (id_emp, cod_unidad, nom_unidad, es_paquete, convuni, logs, fecha_mod)
            VALUES
                (p_id_emp, 'Und', 'Unidad', 'N', 0, v_logs, now());

            -- Motivos de ajuste de stock por defecto (positivo/negativo)
            INSERT INTO public.m_motivoajuste (id_emp, cod_motivo, nom_motivo, signo, activo, cta_inventario, fecha_mod, logs)
            VALUES
                (p_id_emp, 'AjusteP+', 'Ajuste Positivo', 1, true, '1310', now(), v_logs),
                (p_id_emp, 'AjusteP-', 'Ajuste Negativo', -1, true, '1310', now(), v_logs);

            -- Tipos de servicio/costeo por defecto (id_costeo=2 es catalogo global, no por-empresa)
            INSERT INTO public.m_tiposervicio (id_emp, cod_servicio, nom_servicio, id_costeo)
            VALUES
                (p_id_emp, 'Producto', 'Producto', 2),
                (p_id_emp, 'Servicio', 'Servicios', 2);
        END;
        $procedure$;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        CREATE OR REPLACE PROCEDURE public.sp_core_nuevaempresa(IN p_id_emp integer)
         LANGUAGE plpgsql
        AS $procedure$
        DECLARE
            v_logs json;
        BEGIN
            SELECT logs INTO v_logs FROM public.md_empresas WHERE id_emp = p_id_emp;

            INSERT INTO public.m_sucursales (id_emp, cod_sucursal, nom_sucursal, id_ciudad, direccion, telefono, activo, logs, fecha_mod)
            SELECT id_emp, '01', 'Sucursal Principal', cod_ciudad, direccion, telefono, true, v_logs, now()
            FROM public.md_empresas
            WHERE id_emp = p_id_emp;

            INSERT INTO public.m_negocios (id_emp, cod_negocio, nom_negocio, logs, fecha_mod, activo)
            SELECT id_emp, '01', nom_emp, v_logs, now(), true
            FROM public.md_empresas
            WHERE id_emp = p_id_emp;

            INSERT INTO public.m_estados (id_emp, cod_estado, nom_estado, activo, obervacion, fecha_mod, logs)
            VALUES
                (p_id_emp, 'Disponible', 'Disponible en Bodega', true, 'Estado disponible para venta/consumo', now(), v_logs);

            INSERT INTO public.m_unidades (id_emp, cod_unidad, nom_unidad, es_paquete, convuni, logs, fecha_mod)
            VALUES
                (p_id_emp, 'Und', 'Unidad', 'N', 0, v_logs, now());

            INSERT INTO public.m_motivoajuste (id_emp, cod_motivo, nom_motivo, signo, activo, cta_inventario, fecha_mod, logs)
            VALUES
                (p_id_emp, 'AjusteP+', 'Ajuste Positivo', 1, 'S', '1310', now(), v_logs),
                (p_id_emp, 'AjusteP-', 'Ajuste Negativo', -1, 'S', '1310', now(), v_logs);

            INSERT INTO public.m_tiposervicio (id_emp, cod_servicio, nom_servicio, id_costeo)
            VALUES
                (p_id_emp, 'Producto', 'Producto', 2),
                (p_id_emp, 'Servicio', 'Servicios', 2);
        END;
        $procedure$;
    """)
    op.execute("ALTER TABLE public.m_motivoajuste ALTER COLUMN activo TYPE character varying(2) USING (CASE WHEN activo THEN 'S' ELSE 'N' END);")
