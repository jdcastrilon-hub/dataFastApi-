"""carga masiva de precios: t_cargaprecios y td_cargaprecios

Mismo patron que t_cargastock/td_cargastock (carga masiva de stock, dos fases
validar->confirmar), adaptado a precios: sin dimensiones de bodega/proveedor/
negocio, una sola lista de precios por carga, y el detalle guarda unicamente
id_articulo (nunca el codigo crudo tecleado, se resuelve en la validacion) +
precio_venta. Ver project_data_lista_precios_design para el diseño completo
acordado con el usuario.

Revision ID: c83efc0e4854
Revises: 88cf09a12635
Create Date: 2026-08-09 21:10:39.898313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c83efc0e4854'
down_revision: Union[str, Sequence[str], None] = '88cf09a12635'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.t_cargaprecios (
            id_trans        bigint NOT NULL DEFAULT nextval('id_transaccion'),
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_lista        integer NOT NULL REFERENCES public.m_listaprecio(id_lista),
            documento       varchar(10) NOT NULL,
            nro_docum       integer NOT NULL,
            fecha_carga     date NOT NULL,
            observacion     varchar(250) NULL,
            nombre_archivo  varchar(150) NULL,
            vista           varchar(16) NOT NULL,
            fecha_mod       timestamp NOT NULL,
            logs            json NULL,
            PRIMARY KEY (id_trans)
        );
    """)

    op.execute("""
        CREATE TABLE public.td_cargaprecios (
            id_trans        bigint NOT NULL REFERENCES public.t_cargaprecios(id_trans),
            id_articulo     integer NOT NULL,
            linea           integer NOT NULL,
            precio_venta    numeric(20,2) NOT NULL,
            PRIMARY KEY (id_trans, id_articulo, linea)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.td_cargaprecios;")
    op.execute("DROP TABLE IF EXISTS public.t_cargaprecios;")
