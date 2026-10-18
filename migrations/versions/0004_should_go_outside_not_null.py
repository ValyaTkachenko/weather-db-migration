"""Колонка should_go_outside стає обов'язковою (NOT NULL)

Крок 3 з 3. Виконується після того, як програма заповнила колонку.
Якщо залишилися незаповнені записи, міграція зупиняється з поясненням,
щоб не зламати базу.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    empty = op.get_bind().execute(
        sa.text("SELECT COUNT(*) FROM precipitation WHERE should_go_outside IS NULL")
    ).scalar()
    if empty:
        raise RuntimeError(
            f"У {empty} записах should_go_outside ще не заповнено. "
            "Спочатку виконайте: python -m app.cli.fill_go_outside"
        )
    op.alter_column(
        "precipitation",
        "should_go_outside",
        existing_type=sa.Boolean(),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "precipitation",
        "should_go_outside",
        existing_type=sa.Boolean(),
        nullable=True,
    )
