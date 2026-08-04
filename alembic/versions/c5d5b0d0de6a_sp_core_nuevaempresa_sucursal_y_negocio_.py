"""sp_core_nuevaempresa: sucursal y negocio default, reusar logs de la empresa

Dos ajustes sobre el SP creado en 433c60103665 (aplicados primero en vivo
sobre Postgres, esta migracion sincroniza el historial de Alembic con ese
estado real):

1. Se agregan 2 inserts nuevos: sucursal principal (m_sucursales, cod '01') y
   negocio principal (m_negocios, cod '01', nombre = nom_emp de la empresa).

2. El resto de maestros (m_estados/m_unidades/m_motivoajuste) dejan de
   insertar logs='[]' fijo - ese valor rompia la trazabilidad de quien creo
   el registro (quedaba sin auditoria propia) y ademas el logs=[] original
   sin ningun log real no es consistente con como se auditan el resto de
   maestros del sistema (siempre nace con 1 entrada 'Nuevo'). En vez de
   recibir el JSON como parametro nuevo del SP (que obligaria a cambiar la
   firma y el CALL desde repository_empresa.py) o reconstruirlo a mano en
   plpgsql, se lee 1 sola vez con SELECT INTO desde md_empresas.logs (la
   misma fila que ya se creo, en la misma transaccion) y se reusa esa unica
   variable en los 5 inserts - incluye tambien a m_sucursales/m_negocios,
   que hasta ahora repetian el mismo SELECT contra md_empresas por insert.
   m_tiposervicio no tiene columna logs, no aplica.

Revision ID: c5d5b0d0de6a
Revises: 433c60103665
Create Date: 2026-08-03 18:16:48.328680

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d5b0d0de6a'
down_revision: Union[str, Sequence[str], None] = '433c60103665'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
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
                (p_id_emp, 'AjusteP+', 'Ajuste Positivo', 1, 'S', '1310', now(), v_logs),
                (p_id_emp, 'AjusteP-', 'Ajuste Negativo', -1, 'S', '1310', now(), v_logs);

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
        BEGIN
            -- Estados de stock por defecto
            INSERT INTO public.m_estados (id_emp, cod_estado, nom_estado, activo, obervacion, fecha_mod, logs)
            VALUES
                (p_id_emp, 'Disponible', 'Disponible en Bodega', true, 'Estado disponible para venta/consumo', now(), '[]');

            -- Unidad de medida por defecto
            INSERT INTO public.m_unidades (id_emp, cod_unidad, nom_unidad, es_paquete, convuni, logs, fecha_mod)
            VALUES
                (p_id_emp, 'Und', 'Unidad', 'N', 0, '[]', now());

            -- Motivos de ajuste de stock por defecto (positivo/negativo)
            INSERT INTO public.m_motivoajuste (id_emp, cod_motivo, nom_motivo, signo, activo, cta_inventario, fecha_mod, logs)
            VALUES
                (p_id_emp, 'AjusteP+', 'Ajuste Positivo', 1, 'S', '1310', now(), '[]'),
                (p_id_emp, 'AjusteP-', 'Ajuste Negativo', -1, 'S', '1310', now(), '[]');

            -- Tipos de servicio/costeo por defecto (id_costeo=2 es catalogo global, no por-empresa)
            INSERT INTO public.m_tiposervicio (id_emp, cod_servicio, nom_servicio, id_costeo)
            VALUES
                (p_id_emp, 'Producto', 'Producto', 2),
                (p_id_emp, 'Servicio', 'Servicios', 2);
        END;
        $procedure$;
    """)
