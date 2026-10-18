"""Шар доступу до даних: запити до таблиці precipitation."""
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.models import Precipitation


class PrecipitationRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_unfilled(self, limit: int):
        """Записи, у яких ще не пораховано should_go_outside."""
        stmt = (
            select(
                Precipitation.id,
                Precipitation.precip_mm,
                Precipitation.humidity,
                Precipitation.cloud,
            )
            .where(Precipitation.should_go_outside.is_(None))
            .order_by(Precipitation.id)
            .limit(limit)
        )
        return self.session.execute(stmt).all()

    def bulk_update_go_outside(self, values: list[dict]) -> None:
        """Оновлення пачки записів за первинним ключем: [{'id': .., 'should_go_outside': ..}]."""
        if values:
            self.session.execute(update(Precipitation), values)

    def count_by_answer(self) -> list[tuple]:
        stmt = (
            select(Precipitation.should_go_outside, func.count())
            .group_by(Precipitation.should_go_outside)
            .order_by(Precipitation.should_go_outside)
        )
        return self.session.execute(stmt).all()
