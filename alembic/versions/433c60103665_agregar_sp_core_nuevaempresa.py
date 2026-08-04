"""agregar sp_core_nuevaempresa

Reemplaza a _copiar_maestro (repository_empresa.py), que copiaba estos 4
maestros desde una empresa plantilla (id_emp_plantilla). No todo lo que una
empresa nueva necesita se justifica copiar de otra fila real - estos son
catalogos de arranque fijos, asi que quedan hardcodeados en el SP en vez de
depender de que la plantilla siga teniendo esas filas intactas. El SP recibe
unicamente el id_emp de la empresa recien creada.

De paso corrige el "logs=NULL" que _copiar_maestro dejaba en m_estados/
m_unidades/m_motivoajuste (ver docs/tecnica/specs/core/creacion-empresa.md,
"Casos borde del proceso") - se inicializa en '[]' aca. m_tiposervicio no
tiene columna logs, no aplica.

Revision ID: 433c60103665
Revises: 8f002b62bd05
Create Date: 2026-08-03 17:50:30.458699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '433c60103665'
down_revision: Union[str, Sequence[str], None] = '8f002b62bd05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
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


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP PROCEDURE IF EXISTS public.sp_core_nuevaempresa(integer);")
