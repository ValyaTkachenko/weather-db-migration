"""Шар представлення: консольна команда імпорту CSV.

Запуск:
    python -m app.cli.import_csv
    python -m app.cli.import_csv --replace           # перезалити дані
    python -m app.cli.import_csv --path інший.csv
"""
import argparse
import time

from app.config import CSV_PATH
from app.db import SessionLocal
from app.repositories.weather_repository import WeatherRepository
from app.services.csv_import_service import CsvImportService


def main() -> None:
    parser = argparse.ArgumentParser(description="Імпорт погодних даних з CSV у базу")
    parser.add_argument("--path", default=CSV_PATH, help="шлях до CSV-файлу")
    parser.add_argument("--replace", action="store_true", help="видалити старі дані перед імпортом")
    args = parser.parse_args()

    print(f"Імпорт з файлу {args.path}")
    started = time.time()
    with SessionLocal() as session:
        service = CsvImportService(WeatherRepository(session))
        count = service.import_file(args.path, replace=args.replace)
        total = WeatherRepository(session).count()
    print(f"Готово: імпортовано {count} рядків за {time.time() - started:.1f} с.")
    print(f"Усього записів у таблиці weather: {total}")


if __name__ == "__main__":
    main()
