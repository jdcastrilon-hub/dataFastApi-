"""m_confcomercial + m_confcomercial_dctoxrol (configuracion comercial por empresa)

Revision ID: 5c374d540a8b
Revises: 9bbab031a3f4
Create Date: 2026-08-11 00:00:02.000000

m_confcomercial: 1 fila por empresa, configuracion del modulo Comercial.
- precio_cero_editable: si el cajero puede fijar manualmente el precio de un
  articulo cuando la lista de precios no tiene ninguno cargado (hoy siempre
  llega en 0 sin aviso, ver analisis en sesion).
- reimpresion_factura_permitida / id_bodega_devoluciones: placeholders para
  funcionalidades que todavia no existen (reimpresion de factura, nota de
  credito/devolucion de venta) - agregados ahora a peticion explicita del
  usuario para no tener que migrar la tabla de nuevo cuando se construyan.

m_confcomercial_dctoxrol: grilla de "que rol puede aplicar descuento y hasta
cuanto" - vive en Comercial (no en md_rol/Administracion) a proposito, mismo
criterio ya usado para m_listaprecioxuser (permiso de dominio, no de
identidad). Deny by default: un rol ausente de esta tabla no tiene permiso
de descuento. Sin logs/fecha_mod - misma categoria que m_listaprecioxuser
(tabla de permisos pura, no lleva auditoria propia).
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '5c374d540a8b'
down_revision = '9bbab031a3f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.m_confcomercial (
            id_emp                          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            precio_cero_editable             boolean NOT NULL DEFAULT false,
            reimpresion_factura_permitida    boolean NOT NULL DEFAULT false,
            id_bodega_devoluciones           integer NULL REFERENCES public.m_bodegas(id),
            fecha_mod                        timestamp NOT NULL DEFAULT now(),
            logs                             json NULL,
            PRIMARY KEY (id_emp)
        );
    """)

    op.execute("""
        CREATE TABLE public.m_confcomercial_dctoxrol (
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_rol          integer NOT NULL REFERENCES public.md_rol(id_rol),
            max_descuento   numeric(5,2) NOT NULL,
            PRIMARY KEY (id_emp, id_rol)
        );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS public.m_confcomercial_dctoxrol")
    op.execute("DROP TABLE IF EXISTS public.m_confcomercial")
