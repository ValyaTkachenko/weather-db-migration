"""Шар доступу до даних: запити до таблиць weather і precipitation."""
from datetime import date, datetime, time, timedelta
from typing import Optional

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Precipitation, Weather


class WeatherRepository:
    def __init__(self, session: Session):
        self.session = session

    def count(self) -> int:
        return self.session.scalar(select(func.count()).select_from(Weather))

    def delete_all(self) -> None:
        # спочатку дочірня таблиця, потім батьківська
        self.session.execute(delete(Precipitation))
        self.session.execute(delete(Weather))

    def bulk_insert(self, rows: list[Weather]) -> None:
        """Додає пачку записів погоди разом з пов'язаними записами про осади."""
        if rows:
            self.session.add_all(rows)
            self.session.flush()
            self.session.expunge_all()  # звільняємо пам'ять після кожної пачки

    # ---------- пошук (етап 4) ----------

    def find(self, country: str, day: date, city: Optional[str] = None) -> list[Weather]:
        """Усі записи погоди для країни за вказану дату (і, за бажанням, місто).

        Порівняння назв без урахування регістру. Дата шукається як діапазон
        [день 00:00; наступний день 00:00), щоб працював індекс по last_updated.
        """
        start = datetime.combine(day, time.min)
        end = start + timedelta(days=1)
        stmt = (
            select(Weather)
            .options(joinedload(Weather.precipitation))  # дані з обох таблиць одним запитом
            .where(func.lower(Weather.country) == country.strip().lower())
            .where(Weather.last_updated >= start, Weather.last_updated < end)
            .order_by(Weather.location_name, Weather.last_updated)
        )
        if city:
            stmt = stmt.where(func.lower(Weather.location_name) == city.strip().lower())
        return list(self.session.scalars(stmt).unique())

    def available_dates(self, country: str, limit: int = 10) -> list[date]:
        """Найближчі дати, за які є дані по країні (підказка, якщо нічого не знайдено)."""
        day = func.date(Weather.last_updated)
        stmt = (
            select(day)
            .where(func.lower(Weather.country) == country.strip().lower())
            .group_by(day)
            .order_by(day)
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def country_exists(self, country: str) -> bool:
        stmt = select(Weather.id).where(
            func.lower(Weather.country) == country.strip().lower()
        ).limit(1)
        return self.session.scalar(stmt) is not None
