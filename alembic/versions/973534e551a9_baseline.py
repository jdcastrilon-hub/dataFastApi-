"""baseline

Punto de partida de Alembic: describe el esquema tal como existia en Postgres
el dia que se adopto Alembic (80 tablas, 49 funciones/procedimientos, 6
triggers). Generado con scripts/generar_baseline_alembic.py, ya que pg_dump
no esta disponible en este entorno - ver docs/tecnica/setup.md.

Revision ID: 973534e551a9
Revises:
Create Date: 2026-07-27 19:47:15.939946

"""
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '973534e551a9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ARCHIVO_DDL = Path(__file__).with_suffix(".sql")


def upgrade() -> None:
    """Crea las 80 tablas + 49 funciones/procedimientos + 6 triggers tal como
    existian al adoptar Alembic. En el servidor donde esto se escribio, el
    esquema ya existia y esta revision se aplico con `alembic stamp head`
    (nunca se corrio este upgrade() ahi). En un servidor nuevo/vacio (ej. un
    shard adicional), `alembic upgrade head` si ejecuta este DDL completo."""
    op.execute(_ARCHIVO_DDL.read_text(encoding="utf-8"))


def downgrade() -> None:
    """A proposito no revierte nada: bajar de esta revision implicaria
    borrar el esquema completo (80 tablas, funciones, triggers). Si de verdad
    se necesita descartar un servidor de prueba, hacerlo manualmente
    (DROP DATABASE), no vía downgrade."""
    raise NotImplementedError(
        "El downgrade del baseline no esta implementado a proposito - "
        "revertirlo borraria todo el esquema. Ver el docstring de esta migracion."
    )
