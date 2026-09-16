"""notafactura_credito

Revision ID: a4579791d53f
Revises: 033b9788dd26
Create Date: 2026-08-15 11:32:32.803924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4579791d53f'
down_revision: Union[str, Sequence[str], None] = '033b9788dd26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Catalogo de motivos para nota credito - mismo shape que m_motivodevolucion
    # (Compras), pero tabla propia: son motivos de negocio distintos (producto
    # defectuoso, cliente no satisfecho, etc. vs. proveedor envio mal el pedido),
    # mismo criterio de domain-ownership-split ya usado en este proyecto (ej.
    # m_confcomercial_dctoxrol vive en Comercial aunque referencie md_rol).
    op.execute("""
        CREATE TABLE public.m_motivodevolucionventa (
            id              serial PRIMARY KEY,
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            cod_motivo      varchar(10) NOT NULL,
            nom_motivo      varchar(80) NOT NULL,
            -- Si esta marcado, la nota que use este motivo exige id_turno/id_caja
            -- (igual que factura) y genera un GastoCaja real vía movimientocaja.
            -- Si NO esta marcado, el importe de la nota queda como saldo a favor
            -- del cliente (p_saldocliente/s_saldocliente) en vez de salir de caja.
            devuelve_dinero boolean NOT NULL DEFAULT false,
            activo          varchar(2) NOT NULL,
            fecha_mod       timestamp DEFAULT now(),
            logs            json,
            CONSTRAINT m_motivodevolucionventa_unique UNIQUE (id_emp, cod_motivo)
        )
    """)

    # Cabecera de nota credito. id_trans usa la misma secuencia 'id_transaccion'
    # que comparten compras/ajustes/traslados/devoluciones/facturas - por eso
    # id_trans_ref (la factura que se esta devolviendo) puede ser una FK real
    # aunque el origen sea otra tabla: no hace falta duplicar logica de
    # numeracion. documento/nro_docum/serie_docum son la identidad propia de
    # ESTA nota (su propio numerador), separada de id_trans_ref (a que factura
    # referencia) - no se mezclan.
    op.execute("""
        CREATE TABLE public.t_notafactura (
            id_trans        bigint NOT NULL DEFAULT nextval('public.id_transaccion') PRIMARY KEY,
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_cliente      integer NOT NULL,
            id_sucursal     integer NOT NULL REFERENCES public.m_sucursales(id),
            id_trans_ref    bigint NOT NULL,
            id_bodega       integer NOT NULL REFERENCES public.m_bodegas(id),
            id_estado       integer NOT NULL,
            -- Nullable: solo se llenan cuando el motivo elegido tiene
            -- devuelve_dinero=true (reembolso real de caja). Sin FK declarada,
            -- mismo criterio que t_facturas.id_turno/id_caja (t_facturas tampoco
            -- tiene FKs reales en la BD, se resuelven por join explicito).
            id_turno        integer,
            id_caja         integer,
            fec_doc         date NOT NULL,
            documento       varchar(16) NOT NULL,
            nro_docum       integer NOT NULL,
            serie_docum     varchar(8) NOT NULL,
            id_motivo       integer NOT NULL REFERENCES public.m_motivodevolucionventa(id),
            observacion     varchar(250),
            imp_neto        numeric(14,2) NOT NULL,
            -- Los 3 impuestos existen en t_facturas aunque hoy solo se use el 1
            -- (IVA) - se agregan de una vez, no despues, para que el modelo de
            -- nota quede simetrico con factura sin tener que retocarlo cuando
            -- se activen impuesto2/3.
            impuesto1       varchar(6) NOT NULL,
            valor_impuesto1 numeric(14,2) NOT NULL,
            impuesto2       varchar(6) NOT NULL,
            valor_impuesto2 numeric(14,2) NOT NULL,
            impuesto3       varchar(6) NOT NULL,
            valor_impuesto3 numeric(14,2) NOT NULL,
            imp_total       numeric(14,2) NOT NULL,
            vista           varchar(16) NOT NULL,
            -- Reservado para un futuro flujo de autorizacion (Pendiente/Aprobada/
            -- Rechazada), mismo criterio que t_devolucioncompras.status - hoy sin
            -- logica, la nota impacta stock/saldo de inmediato al guardar.
            status          varchar(2) NOT NULL,
            fecha_mod       timestamp NOT NULL DEFAULT now(),
            logs            json,
            CONSTRAINT t_notafactura_factura_origen_fk
                FOREIGN KEY (id_emp, id_trans_ref) REFERENCES public.t_facturas (id_emp, id_trans)
        )
    """)

    # Detalle de nota credito - shape de linea igual a td_facturas (precio +
    # impuesto1, no costo como td_devolucioncompras) porque la nota es un
    # documento de cara al cliente (afecta su saldo/IVA), no un ajuste interno
    # de costo.
    op.execute("""
        CREATE TABLE public.td_notafactura (
            id_trans        bigint NOT NULL REFERENCES public.t_notafactura(id_trans),
            linea           integer NOT NULL,
            id_articulo     integer NOT NULL,
            id_codbarra     integer NOT NULL,
            id_lote         integer NOT NULL DEFAULT 0,
            cantidad        integer NOT NULL,
            precio_unit     numeric(14,2) NOT NULL,
            impuesto1       varchar(6) NOT NULL,
            id_tasaimp1     integer NOT NULL,
            valor_impuesto1 numeric(14,2) NOT NULL,
            impuesto2       varchar(6) NOT NULL,
            id_tasaimp2     integer NOT NULL,
            valor_impuesto2 numeric(14,2) NOT NULL,
            impuesto3       varchar(6) NOT NULL,
            id_tasaimp3     integer NOT NULL,
            valor_impuesto3 numeric(14,2) NOT NULL,
            imp_neto        numeric(14,2) NOT NULL,
            imp_total       numeric(14,2) NOT NULL,
            PRIMARY KEY (id_trans, linea)
        )
    """)


    # Ledger de saldo a favor del cliente - mismo patron ya usado en este
    # proyecto para p_stock/s_stkbodegas y p_costos/s_costoxbodegas (columnas
    # calcadas de esas dos, revisadas en vivo antes de escribir esto): p_ es el
    # historico inmutable (un movimiento = una fila, nunca se actualiza ni se
    # borra), s_ es el snapshot (una fila por cliente con el saldo YA sumado),
    # para no tener que hacer SUM sobre el historico cada vez que se necesita
    # saber cuanto saldo tiene un cliente. Alimentan p_saldocliente: notas
    # credito sin devuelve_dinero (signo +1) y a futuro anticipos de reserva
    # (signo +1); lo consume aplicar saldo como medio de pago en una factura
    # futura (signo -1). El trigger/SP que mantiene sincronizado s_saldocliente
    # a partir de p_saldocliente (igual que sp_costeo_impacto_costeoxbodega para
    # stock/costos) se construye junto con la logica de negocio de la nota, no
    # en este script - esto es solo la estructura de tablas.
    op.execute("""
        CREATE TABLE public.p_saldocliente (
            id_trans        bigint NOT NULL,
            linea           integer NOT NULL DEFAULT 1,
            id_emp          integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_cliente      integer NOT NULL,
            documento       varchar(16) NOT NULL,
            nro_docum       integer NOT NULL,
            documento_ref   varchar(16),
            nro_ref         integer,
            fec_doc         date NOT NULL,
            importe         numeric(14,2) NOT NULL,
            -- +1 suma al saldo a favor (nota credito sin devuelve_dinero, anticipo
            -- de reserva); -1 lo consume (se aplico como medio de pago en una
            -- factura).
            signo           integer NOT NULL,
            vista           varchar(16) NOT NULL,
            fecha_mod       timestamp NOT NULL DEFAULT now(),
            PRIMARY KEY (id_trans, linea)
        )
    """)

    op.execute("""
        CREATE TABLE public.s_saldocliente (
            id_emp      integer NOT NULL REFERENCES public.md_empresas(id_emp),
            id_cliente  integer NOT NULL,
            saldo       numeric(14,2) NOT NULL DEFAULT 0,
            PRIMARY KEY (id_emp, id_cliente)
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS public.s_saldocliente")
    op.execute("DROP TABLE IF EXISTS public.p_saldocliente")
    op.execute("DROP TABLE IF EXISTS public.td_notafactura")
    op.execute("DROP TABLE IF EXISTS public.t_notafactura")
    op.execute("DROP TABLE IF EXISTS public.m_motivodevolucionventa")
