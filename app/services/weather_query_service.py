"""Шар бізнес-логіки: пошук погоди за країною і датою."""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

from app.models import Weather
from app.repositories.weather_repository import WeatherRepository


@dataclass
class SearchResult:
    records: list[Weather]
    country_known: bool = True
    suggested_dates: list[date] = field(default_factory=list)


class WeatherQueryService:
    def __init__(self, repository: WeatherRepository):
        self.repository = repository

    @staticmethod
    def parse_date(text: str) -> date:
        """Приймає дату у форматі РРРР-ММ-ДД або ДД.ММ.РРРР."""
        text = text.strip()
        for fmt in ("%Y-%m-%d", "%d.%m.%Y"):
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        raise ValueError(f"Невірний формат дати: {text!r}. Приклад: 2024-05-16 або 16.05.2024")

    def search(self, country: str, day: date, city: Optional[str] = None) -> SearchResult:
        records = self.repository.find(country, day, city)
        if records:
            return SearchResult(records)
        if not self.repository.country_exists(country):
            return SearchResult([], country_known=False)
        return SearchResult([], suggested_dates=self.repository.available_dates(country))
