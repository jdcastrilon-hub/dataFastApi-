"""td_compras.imp_precio_vta + indice unico m_listaprecio.es_general + sp_compradirecta

Revision ID: 9f2c6a1e4d78
Revises: 7a1d9e5f2c4b
Create Date: 2026-09-13 00:00:00.000000

Habilita que el usuario digite el precio de venta directamente en Compra
Directa (condicionado a m_confcompras.act_precio_compra, ver frontend) y que
ese precio impacte p_precios (lista general de la empresa), igual criterio
que ya usa Carga de Stock (repository_cargastock.py) para el mismo caso.

- td_compras.imp_precio_vta: numeric(14,2) NOT NULL DEFAULT 0. 0 = "no se
  definio precio de venta para esta linea" (sentinela, no un precio real) -
  sp_compradirecta solo impacta p_precios cuando es > 0.
- m_listaprecio: indice unico parcial que garantiza como maximo UNA lista
  con es_general=true y activo=true por empresa. Gap pre-existente (nada lo
  impedia hasta ahora) que se corrige de paso porque sp_compradirecta pasa a
  depender de que esa lista sea inequivoca.
- sp_compradirecta: nuevo parametro p_id_lista (resuelto y validado en
  Python ANTES de llamar el SP - ver repository_compras.py - por eso el SP
  no vuelve a buscarlo ni valida su existencia, solo lo usa). Borra e
  reinserta p_precios del id_trans (mismo patron ya usado con p_stock/
  p_costos, idempotente en cada edicion) e impacta unicamente las lineas con
  imp_precio_vta > 0. p_precios no tiene trigger de DELETE (a diferencia de
  p_costos) - borrar sus filas no revierte el precio actual del articulo en
  s_precioxarticulo, es una decision explicita (ver analisis en sesion): el
  precio de venta no se revierte automaticamente al eliminar/editar una
  compra, porque para cuando eso pasa ya pudo haber ventas reales con ese
  precio.
"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '9f2c6a1e4d78'
down_revision = '7a1d9e5f2c4b'
branch_labels = None
depends_on = None


SP_ANTERIOR = """
CREATE OR REPLACE PROCEDURE public.sp_compradirecta(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying)
 LANGUAGE plpgsql
AS $procedure$
        BEGIN
            INSERT INTO public.m_artxcodigobarra(
            id_articulo, id_codbarra, cod_barra, ref_barra)
            select id_articulo, id_codbarra, cod_barra, ref_barra
            FROM public.td_comprasnewcodbarra where id_trans=parm_trans;

            INSERT INTO public.m_lotes(id, id_articulo, codigo_lote, fec_vencimiento)
            SELECT id_lote, id_articulo, codigo_lote, fec_vencimiento
            FROM public.td_comprasnuevolote WHERE id_trans=parm_trans;

            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;

            INSERT INTO public.p_costos(
            id_trans, linea, id_emp,id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref, id_proveedor, fec_doc,
            id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional, stock_actual, stock_nuevo,
            imp_costo_total, imp_costo_unitario, vista, usuario_mod, fecha_mod)
            select A.id_trans,B.linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,a.id_proveedor,A.fec_doc,
            b.id_articulo,b.cantidad,1 signo,
            COALESCE(D.imp_costo_unitario,0) imp_costo_actual,
            B.costo_unit imp_costo_nuevo,
            0 imp_costo_adicional,
            COALESCE(D.cantidad, 0) stock_actual,
            (B.cantidad+COALESCE(D.cantidad, 0)) stock_nuevo,
            cast((B.costo_unit*B.cantidad) as numeric(20,2)) imp_costo_total,
            cast(((COALESCE(D.cantidad,0)*COALESCE(D.imp_costo_unitario,0))+(B.costo_unit*B.cantidad))/NULLIF((B.cantidad+COALESCE(D.cantidad,0)),0) as numeric(20,2)) imp_costo_unitario,
            A.vista, p_usuario, A.fecha_mod
            from t_compras A
            inner join td_compras B On a.id_trans=B.id_trans
            inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
            left join s_costoxbodegas D on A.id_bodega=D.id_bodega and B.id_articulo=D.id_articulo
            where A.id_trans=parm_trans;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
            B.cantidad,1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod,p_usuario
            from t_compras A
            inner join td_compras B On a.id_trans=B.id_trans
            inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
            where A.id_trans=parm_trans;

        END;
        $procedure$
"""

SP_NUEVO = """
CREATE OR REPLACE PROCEDURE public.sp_compradirecta(IN operacion character varying, IN parm_trans integer, IN p_usuario character varying DEFAULT NULL::character varying, IN p_id_lista integer DEFAULT NULL::integer)
 LANGUAGE plpgsql
AS $procedure$
        BEGIN
            INSERT INTO public.m_artxcodigobarra(
            id_articulo, id_codbarra, cod_barra, ref_barra)
            select id_articulo, id_codbarra, cod_barra, ref_barra
            FROM public.td_comprasnewcodbarra where id_trans=parm_trans;

            INSERT INTO public.m_lotes(id, id_articulo, codigo_lote, fec_vencimiento)
            SELECT id_lote, id_articulo, codigo_lote, fec_vencimiento
            FROM public.td_comprasnuevolote WHERE id_trans=parm_trans;

            delete from p_stock where id_trans=parm_trans;
            delete from p_costos where id_trans=parm_trans;
            delete from p_precios where id_trans=parm_trans;

            INSERT INTO public.p_costos(
            id_trans, linea, id_emp,id_bodega, id_trans_ref, documento, nro_docum, documento_ref, nro_docum_ref, id_proveedor, fec_doc,
            id_articulo, cantidad, signo, imp_costo_actual, imp_costo_nuevo, imp_costo_adicional, stock_actual, stock_nuevo,
            imp_costo_total, imp_costo_unitario, vista, usuario_mod, fecha_mod)
            select A.id_trans,B.linea,a.id_emp,A.id_bodega,0 id_trans_ref,A.documento,a.nro_docum,null,null,a.id_proveedor,A.fec_doc,
            b.id_articulo,b.cantidad,1 signo,
            COALESCE(D.imp_costo_unitario,0) imp_costo_actual,
            B.costo_unit imp_costo_nuevo,
            0 imp_costo_adicional,
            COALESCE(D.cantidad, 0) stock_actual,
            (B.cantidad+COALESCE(D.cantidad, 0)) stock_nuevo,
            cast((B.costo_unit*B.cantidad) as numeric(20,2)) imp_costo_total,
            cast(((COALESCE(D.cantidad,0)*COALESCE(D.imp_costo_unitario,0))+(B.costo_unit*B.cantidad))/NULLIF((B.cantidad+COALESCE(D.cantidad,0)),0) as numeric(20,2)) imp_costo_unitario,
            A.vista, p_usuario, A.fecha_mod
            from t_compras A
            inner join td_compras B On a.id_trans=B.id_trans
            inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
            left join s_costoxbodegas D on A.id_bodega=D.id_bodega and B.id_articulo=D.id_articulo
            where A.id_trans=parm_trans;

            insert into p_stock
            select A.id_trans,A.id_emp,A.documento,a.nro_docum,null,null,A.fec_doc,
            b.id_articulo,b.id_codbarra,a.id_bodega,a.id_estado,B.id_lote,0 id_ubicacion,
            B.cantidad,1 signo,null,A.vista,B.linea,'Imp',A.fecha_mod,p_usuario
            from t_compras A
            inner join td_compras B On a.id_trans=B.id_trans
            inner join m_artxcodigobarra C on B.id_articulo=C.id_articulo and B.id_codbarra=C.id_codbarra
            where A.id_trans=parm_trans;

            -- Precio de venta (opcional por linea): solo si la empresa activo
            -- act_precio_compra y la linea trae imp_precio_vta > 0. p_id_lista
            -- ya viene resuelto y validado desde Python (repository_compras.py)
            -- - si por algun motivo llega NULL, el "AND p_id_lista IS NOT NULL"
            -- es una red de seguridad, no la validacion real. El trigger
            -- ins_p_precios actualiza el snapshot s_precioxarticulo y
            -- ins_p_precios_reglas propaga a listas con regla de categoria activa.
            -- ORDER BY B.linea: si el mismo articulo aparece en 2+ lineas de la
            -- misma compra con precios distintos, gana la de mayor numero de
            -- linea de forma deterministica (no el orden fisico que Postgres
            -- elija para el INSERT...SELECT, que no esta garantizado sin esto).
            INSERT INTO public.p_precios(
            id_trans, linea, id_emp, id_lista, id_articulo,
            precio_anterior, precio_nuevo, origen, usuario_mod, fecha_mod)
            select A.id_trans, B.linea, A.id_emp, p_id_lista, B.id_articulo,
            S.precio_venta, B.imp_precio_vta, 'COMPRA_DIRECTA', p_usuario, A.fecha_mod
            from t_compras A
            inner join td_compras B on A.id_trans=B.id_trans
            left join s_precioxarticulo S on S.id_lista=p_id_lista and S.id_articulo=B.id_articulo
            where A.id_trans=parm_trans
              and B.imp_precio_vta > 0
              and p_id_lista is not null
            order by B.linea;

        END;
        $procedure$
"""


def upgrade() -> None:
    op.execute("""
        ALTER TABLE public.td_compras
        ADD COLUMN imp_precio_vta numeric(14,2) NOT NULL DEFAULT 0;
    """)

    op.execute("""
        CREATE UNIQUE INDEX m_listaprecio_unica_general
        ON public.m_listaprecio (id_emp)
        WHERE es_general = true AND activo = true;
    """)

    # CREATE OR REPLACE PROCEDURE no reemplaza una firma con distinta cantidad
    # de parametros - crea un OVERLOAD nuevo y deja la version vieja (3
    # parametros) viva y llamable en paralelo. Hay que borrarla explicitamente
    # antes de crear la de 4 parametros.
    op.execute("DROP PROCEDURE IF EXISTS public.sp_compradirecta(character varying, integer, character varying)")
    op.execute(SP_NUEVO)


def downgrade() -> None:
    op.execute("DROP PROCEDURE IF EXISTS public.sp_compradirecta(character varying, integer, character varying, integer)")
    op.execute(SP_ANTERIOR)
    op.execute("DROP INDEX IF EXISTS public.m_listaprecio_unica_general")
    op.execute("ALTER TABLE public.td_compras DROP COLUMN IF EXISTS imp_precio_vta")
