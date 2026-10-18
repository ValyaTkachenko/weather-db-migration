"""Дробові колонки: FLOAT -> DOUBLE для сумісності PostgreSQL і MySQL

Проблема, виявлена при переході на MySQL:
  - у PostgreSQL тип FLOAT = double precision (8 байт, ~15 значущих цифр);
  - у MySQL тип FLOAT = одинарна точність (4 байти, ~7 значущих цифр).
Тобто ті самі міграції створювали в двох СУБД колонки різної точності,
і дробові значення в MySQL могли б трохи відрізнятися.
Явний тип DOUBLE дає однакову точність в обох базах.
У PostgreSQL ця міграція фактично нічого не змінює (тип уже double precision).

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

FLOAT_COLUMNS = (
    ("weather", "wind_kph"),
    ("weather", "temperature_celsius"),
    ("precipitation", "precip_mm"),
    ("precipitation", "precip_in"),
)


def upgrade() -> None:
    for table, column in FLOAT_COLUMNS:
        op.alter_column(
            table, column,
            existing_type=sa.Float(),
            type_=sa.Double(),
            existing_nullable=True,
        )


def downgrade() -> None:
    for table, column in FLOAT_COLUMNS:
        op.alter_column(
            table, column,
            existing_type=sa.Double(),
            type_=sa.Float(),
            existing_nullable=True,
        )
