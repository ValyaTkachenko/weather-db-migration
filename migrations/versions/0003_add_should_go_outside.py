"""Додавання колонки should_go_outside ("Чи варто виходити на вулицю")

Крок 1 з 3. Колонка додається порожньою (NULL) і БЕЗ значення за замовчуванням:
відповідь залежить від даних кожного запису, тому будь-яке фіксоване
значення (true чи false) було б неправдивим для частини записів.
Заповнює колонку програма (шар сервісів): python -m app.cli.fill_go_outside

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "precipitation",
        sa.Column("should_go_outside", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("precipitation", "should_go_outside")
