"""Шар бізнес-логіки: перенесення даних між базами (PostgreSQL -> MySQL)
і порівняння двох баз.

Структуру цільової бази створюють ті самі міграції Alembic
(alembic upgrade head), а цей сервіс лише копіює дані.
Таблиці описані в ORM-моделях, тому код однаковий для будь-якої СУБД.
"""
from sqlalchemy import Engine, delete, func, insert, select, text

from app.models import Precipitation, Weather

# Порядок важливий: спочатку батьківська таблиця, потім дочірня (зовнішній ключ)
TABLES = [Weather.__table__, Precipitation.__table__]

# Контрольні запити - синтаксис, який однаково працює в PostgreSQL і MySQL
CHECKS = [
    ("Версія міграції", "SELECT version_num FROM alembic_version"),
    ("Записів у weather", "SELECT COUNT(*) FROM weather"),
    ("Записів у precipitation", "SELECT COUNT(*) FROM precipitation"),
    ("Кількість країн", "SELECT COUNT(DISTINCT country) FROM weather"),
    ("Перша дата", "SELECT MIN(last_updated) FROM weather"),
    ("Остання дата", "SELECT MAX(last_updated) FROM weather"),
    ("Сума wind_kph", "SELECT CAST(SUM(wind_kph) AS DECIMAL(20,2)) FROM weather"),
    ("Сума temperature_celsius",
     "SELECT CAST(SUM(temperature_celsius) AS DECIMAL(20,2)) FROM weather"),
    ("Сума precip_mm", "SELECT CAST(SUM(precip_mm) AS DECIMAL(20,2)) FROM precipitation"),
    ("Середня вологість", "SELECT CAST(AVG(humidity) AS DECIMAL(10,2)) FROM precipitation"),
    ("Середня хмарність", "SELECT CAST(AVG(cloud) AS DECIMAL(10,2)) FROM precipitation"),
    ("Можна виходити (true)",
     "SELECT COUNT(*) FROM precipitation WHERE should_go_outside = TRUE"),
    ("Краще вдома (false)",
     "SELECT COUNT(*) FROM precipitation WHERE should_go_outside = FALSE"),
]


class TransferService:
    def __init__(self, source: Engine, target: Engine):
        self.source = source
        self.target = target

    def target_count(self) -> int:
        with self.target.connect() as conn:
            return conn.scalar(select(func.count()).select_from(Weather.__table__))

    def clear_target(self) -> None:
        with self.target.begin() as conn:
            for table in reversed(TABLES):
                conn.execute(delete(table))

    def transfer(self, batch_size: int = 5000) -> dict[str, int]:
        """Копіює всі таблиці пачками, зберігаючи ідентифікатори (id) записів."""
        copied: dict[str, int] = {}
        with self.source.connect() as src:
            for table in TABLES:
                total = 0
                result = src.execution_options(stream_results=True).execute(
                    select(table).order_by(table.c.id)
                )
                for part in result.mappings().partitions(batch_size):
                    rows = [dict(row) for row in part]
                    with self.target.begin() as dst:
                        dst.execute(insert(table), rows)
                    total += len(rows)
                    print(f"  {table.name}: перенесено {total} рядків...")
                copied[table.name] = total
        return copied


def run_checks(engine: Engine) -> list:
    with engine.connect() as conn:
        return [conn.execute(text(sql)).scalar() for _, sql in CHECKS]
