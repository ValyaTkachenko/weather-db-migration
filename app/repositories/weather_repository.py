"""Шар доступу до даних: усі запити до таблиці weather."""
from sqlalchemy import delete, func, insert, select
from sqlalchemy.orm import Session

from app.models import Weather


class WeatherRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        return self.session.scalar(select(func.count()).select_from(Weather))

    def delete_all(self) -> None:
        self.session.execute(delete(Weather))

    def bulk_insert(self, rows: list[dict]) -> None:
        """Вставка пачки рядків одним запитом (швидко для ~100 тис. записів)."""
        if rows:
            self.session.execute(insert(Weather), rows)
