"""Рефакторинг: винесення даних про осади в окрему таблицю precipitation

Порядок дій гарантує, що дані не втрачаються:
  1) створюємо нову таблицю precipitation;
  2) КОПІЮЄМО в неї дані з weather (INSERT ... SELECT);
  3) лише після цього видаляємо старі колонки з weather.
Downgrade робить усе у зворотному порядку, теж без втрати даних.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

MOVED_COLUMNS = ("precip_mm", "precip_in", "humidity", "cloud")


def upgrade() -> None:
    # 1. Нова таблиця
    op.create_table(
        "precipitation",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "weather_id",
            sa.Integer(),
            sa.ForeignKey("weather.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("precip_mm", sa.Float(), nullable=True),
        sa.Column("precip_in", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Integer(), nullable=True),
        sa.Column("cloud", sa.Integer(), nullable=True),
    )

    # 2. Перенесення даних (один SQL-запит, працює і в PostgreSQL, і в MySQL)
    op.execute(
        """
        INSERT INTO precipitation (weather_id, precip_mm, precip_in, humidity, cloud)
        SELECT id, precip_mm, precip_in, humidity, cloud
        FROM weather
        """
    )

    # 3. Видалення старих колонок з weather
    for column in MOVED_COLUMNS:
        op.drop_column("weather", column)


def downgrade() -> None:
    # 1. Повертаємо колонки в weather
    op.add_column("weather", sa.Column("precip_mm", sa.Float(), nullable=True))
    op.add_column("weather", sa.Column("precip_in", sa.Float(), nullable=True))
    op.add_column("weather", sa.Column("humidity", sa.Integer(), nullable=True))
    op.add_column("weather", sa.Column("cloud", sa.Integer(), nullable=True))

    # 2. Повертаємо дані (підзапити - синтаксис, сумісний з PostgreSQL і MySQL)
    op.execute(
        """
        UPDATE weather SET
            precip_mm = (SELECT p.precip_mm FROM precipitation p WHERE p.weather_id = weather.id),
            precip_in = (SELECT p.precip_in FROM precipitation p WHERE p.weather_id = weather.id),
            humidity  = (SELECT p.humidity  FROM precipitation p WHERE p.weather_id = weather.id),
            cloud     = (SELECT p.cloud     FROM precipitation p WHERE p.weather_id = weather.id)
        """
    )

    # 3. Видаляємо таблицю precipitation
    op.drop_table("precipitation")
