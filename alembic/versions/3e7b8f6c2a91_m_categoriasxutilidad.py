"""m_categoriasxutilidad (utilidad % sugerida por categoria/subcategoria)

Revision ID: 3e7b8f6c2a91
Revises: 9f2c6a1e4d78
Create Date: 2026-09-13 00:00:00.000000

Maestro CRUD tradicional (lista + formulario, lo administra el rol
Administrador, no el SuperAdmin de m_confcompras) que define un % de utilidad
(markup sobre costo) sugerido por categoria o por subcategoria - usado a
futuro para prellenar "Precio de Venta" en Compra Directa cuando se digita el
costo de una linea (jerarquia: subcategoria -> categoria -> general, este
ultimo en m_confcompras).

- id_subcategoria NULL = la fila aplica a TODA la categoria (el frontend lo
  expone como "Toda la categoria", una opcion explicita del combo, no un
  campo vacio).
- id_subcategoria con valor = la fila es una excepcion para esa subcategoria
  puntual, que pisa el % de la categoria completa.
- Como máximo UNA fila "toda la categoria" por (empresa, categoria) - indice
  unico parcial, mismo criterio ya usado con m_listaprecio_unica_general
  (migracion 9f2c6a1e4d78). Como maximo una fila por (empresa, categoria,
  subcategoria) para el caso de excepcion puntual.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '3e7b8f6c2a91'
down_revision = '9f2c6a1e4d78'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.m_categoriasxutilidad (
            id                  serial PRIMARY KEY,
            id_emp              integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_categoria        integer NOT NULL REFERENCES public.m_categorias(id),
            id_subcategoria     integer NULL REFERENCES public.m_subcategorias(id),
            porc_utilidad       numeric(5,2) NOT NULL,
            activo              boolean NOT NULL DEFAULT true,
            fecha_mod           timestamp NOT NULL DEFAULT now(),
            logs                json NULL
        );
    """)

    op.execute("""
        CREATE UNIQUE INDEX m_categoriasxutilidad_unica_categoria
        ON public.m_categoriasxutilidad (id_emp, id_categoria)
        WHERE id_subcategoria IS NULL;
    """)

    op.execute("""
        CREATE UNIQUE INDEX m_categoriasxutilidad_unica_subcategoria
        ON public.m_categoriasxutilidad (id_emp, id_categoria, id_subcategoria)
        WHERE id_subcategoria IS NOT NULL;
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.m_categoriasxutilidad")
