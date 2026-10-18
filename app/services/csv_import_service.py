"""Шар бізнес-логіки: зчитування CSV і запис у базу через репозиторій.

CSV читається повністю, але в базу потрапляють лише колонки,
описані в ORM-моделі. Решта колонок просто ігнорується.
"""
import csv
from pathlib import Path

from app.repositories.weather_repository import WeatherRepository
from app.services.parsers import (
    parse_datetime,
    parse_float,
    parse_int,
    parse_time,
    parse_wind_direction,
)

# колонка в моделі -> (колонка в CSV, функція перетворення)
COLUMN_MAP = {
    "country": ("country", str.strip),
    "location_name": ("location_name", str.strip),
    "last_updated": ("last_updated", parse_datetime),
    "wind_degree": ("wind_degree", parse_int),
    "wind_kph": ("wind_kph", parse_float),
    "wind_direction": ("wind_direction", parse_wind_direction),
    "sunrise": ("sunrise", parse_time),
    "temperature_celsius": ("temperature_celsius", parse_float),
    "condition_text": ("condition_text", str.strip),
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
        batch: list[dict] = []
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
                    batch.clear()
                    print(f"  завантажено {imported} рядків...")
            self.repository.bulk_insert(batch)
            imported += len(batch)

        self.repository.session.commit()
        return imported

    @staticmethod
    def _check_header(header: list[str]) -> None:
        missing = [csv_col for csv_col, _ in COLUMN_MAP.values() if csv_col not in header]
        if missing:
            raise ValueError(
                "У CSV немає колонок: " + ", ".join(missing)
                + "\nНаявні колонки: " + ", ".join(header)
            )

    @staticmethod
    def _convert(raw: dict) -> dict:
        row = {}
        for model_col, (csv_col, convert) in COLUMN_MAP.items():
            value = raw.get(csv_col)
            row[model_col] = convert(value) if value is not None else None
        if not row["country"] or row["last_updated"] is None:
            raise ValueError("порожня країна або дата")
        return row
