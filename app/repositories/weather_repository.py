"""Шар доступу до даних: запити до таблиць weather і precipitation."""
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

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
