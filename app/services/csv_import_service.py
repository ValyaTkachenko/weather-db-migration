"""Шар бізнес-логіки: зчитування CSV і запис у базу через репозиторій.

CSV читається повністю, але в базу потрапляють лише колонки,
описані в ORM-моделях. Решта колонок просто ігнорується.

Етап 2: кожен рядок CSV тепер розкладається на два об'єкти -
Weather (загальні дані) і Precipitation (дані про осади).
"""
import csv
from pathlib import Path

from app.models import Precipitation, Weather
from app.repositories.weather_repository import WeatherRepository
from app.services.parsers import (
    parse_datetime,
    parse_float,
    parse_int,
    parse_time,
    parse_wind_direction,
)

# колонка в моделі Weather -> (колонка в CSV, функція перетворення)
WEATHER_COLUMNS = {
    "country": ("country", str.strip),
    "location_name": ("location_name", str.strip),
    "last_updated": ("last_updated", parse_datetime),
    "wind_degree": ("wind_degree", parse_int),
    "wind_kph": ("wind_kph", parse_float),
    "wind_direction": ("wind_direction", parse_wind_direction),
    "sunrise": ("sunrise", parse_time),
    "temperature_celsius": ("temperature_celsius", parse_float),
    "condition_text": ("condition_text", str.strip),
}

# колонка в моделі Precipitation -> (колонка в CSV, функція перетворення)
PRECIPITATION_COLUMNS = {
    "precip_mm": ("precip_mm", parse_float),
    "precip_in": ("precip_in", parse_float),
    "humidity": ("humidity", parse_int),
    "cloud": ("cloud", parse_int),
}


class CsvImportService:
    def __init__(self, repository: WeatherRepository):
        self.repository = repository

    def import_file(self, path: str, replace: bool = False, batch_size: int = 2000) -> int:
        csv_path = Path(path)
        if not csv_path.exists():
            raise FileNotFoundError(f"Файл не знайдено: {csv_path.resolve()}")

        existing = self.repository.count()
        if existing and not replace:
            raise RuntimeError(
                f"У таблиці вже є {existing} записів. "
                "Щоб перезавантажити дані, запустіть з параметром --replace."
            )
        if replace:
            self.repository.delete_all()

        imported = 0
        batch: list[Weather] = []
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            self._check_header(reader.fieldnames or [])
            for line_no, raw in enumerate(reader, start=2):
                try:
                    batch.append(self._convert(raw))
                except (ValueError, TypeError) as exc:
                    print(f"  рядок {line_no} пропущено: {exc}")
                    continue
                if len(batch) >= batch_size:
                    self.repository.bulk_insert(batch)
                    imported += len(batch)
                    batch = []
                    print(f"  завантажено {imported} рядків...")
            self.repository.bulk_insert(batch)
            imported += len(batch)

        self.repository.session.commit()
        return imported

    @staticmethod
    def _check_header(header: list[str]) -> None:
        needed = [c for c, _ in WEATHER_COLUMNS.values()] + [
            c for c, _ in PRECIPITATION_COLUMNS.values()
        ]
        missing = [c for c in needed if c not in header]
        if missing:
            raise ValueError(
                "У CSV немає колонок: " + ", ".join(missing)
                + "\nНаявні колонки: " + ", ".join(header)
            )

    @staticmethod
    def _extract(raw: dict, columns: dict) -> dict:
        result = {}
        for model_col, (csv_col, convert) in columns.items():
            value = raw.get(csv_col)
            result[model_col] = convert(value) if value is not None else None
        return result

    def _convert(self, raw: dict) -> Weather:
        weather_data = self._extract(raw, WEATHER_COLUMNS)
        if not weather_data["country"] or weather_data["last_updated"] is None:
            raise ValueError("порожня країна або дата")
        weather = Weather(**weather_data)
        weather.precipitation = Precipitation(**self._extract(raw, PRECIPITATION_COLUMNS))
        return weather
