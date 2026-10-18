"""Створення таблиці weather (усі дані в одній таблиці)

Revision ID: 0001
Revises:
Create Date: 2026-10-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

WIND_DIRECTIONS = (
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
)


def upgrade() -> None:
    op.create_table(
        "weather",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("location_name", sa.String(255), nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=False),
        sa.Column("wind_degree", sa.Integer(), nullable=True),
        sa.Column("wind_kph", sa.Float(), nullable=True),
        sa.Column(
            "wind_direction",
            sa.Enum(*WIND_DIRECTIONS, name="wind_direction_enum"),
            nullable=True,
        ),
        sa.Column("sunrise", sa.Time(), nullable=True),
        sa.Column("temperature_celsius", sa.Float(), nullable=True),
        sa.Column("condition_text", sa.String(100), nullable=True),
        sa.Column("precip_mm", sa.Float(), nullable=True),
        sa.Column("precip_in", sa.Float(), nullable=True),
        sa.Column("humidity", sa.Integer(), nullable=True),
        sa.Column("cloud", sa.Integer(), nullable=True),
    )
    op.create_index("ix_weather_country", "weather", ["country"])
    op.create_index("ix_weather_last_updated", "weather", ["last_updated"])


def downgrade() -> None:
    op.drop_index("ix_weather_last_updated", table_name="weather")
    op.drop_index("ix_weather_country", table_name="weather")
    op.drop_table("weather")
    # У PostgreSQL enum - окремий тип, його треба видалити окремо.
    # У MySQL enum вбудований у колонку, тому checkfirst нічого не зламає.
    sa.Enum(name="wind_direction_enum").drop(op.get_bind(), checkfirst=True)
