"""Шар представлення: пошук погоди в консолі.

Запуск з параметрами:
    python -m app.cli.search --country Ukraine --date 2024-05-16
    python -m app.cli.search --country Ukraine --date 16.05.2024 --city Kyiv
Або без параметрів - програма сама спитає країну, дату і місто:
    python -m app.cli.search
"""
import argparse

from app.db import SessionLocal
from app.models import Weather
from app.repositories.weather_repository import WeatherRepository
from app.services.weather_query_service import WeatherQueryService


def _fmt(value, unit: str = "") -> str:
    if value is None:
        return "-"
    return f"{value}{unit}"


def print_record(w: Weather) -> None:
    p = w.precipitation
    print("=" * 60)
    print(f"{w.location_name}, {w.country}   ({w.last_updated:%Y-%m-%d %H:%M})")
    print("-" * 60)
    print(f"  Погода:            {_fmt(w.condition_text)}")
    print(f"  Температура:       {_fmt(w.temperature_celsius, ' °C')}")
    print(f"  Вітер:             {_fmt(w.wind_kph, ' км/год')}, "
          f"напрямок {w.wind_direction.value if w.wind_direction else '-'} "
          f"({_fmt(w.wind_degree, '°')})")
    print(f"  Схід сонця:        {w.sunrise.strftime('%H:%M') if w.sunrise else '-'}")
    if p is not None:
        print(f"  Опади:             {_fmt(p.precip_mm, ' мм')} ({_fmt(p.precip_in, ' in')})")
        print(f"  Вологість:         {_fmt(p.humidity, ' %')}")
        print(f"  Хмарність:         {_fmt(p.cloud, ' %')}")
        answer = "ТАК" if p.should_go_outside else "НІ, краще залишитися вдома"
        print(f"  Чи варто виходити: {answer}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Пошук погоди за країною і датою")
    parser.add_argument("--country", help="країна англійською, напр. Ukraine")
    parser.add_argument("--date", help="дата: 2024-05-16 або 16.05.2024")
    parser.add_argument("--city", help="місто (необов'язково), напр. Kyiv")
    args = parser.parse_args()

    country = args.country or input("Країна (англійською, напр. Ukraine): ")
    date_text = args.date or input("Дата (напр. 2024-05-16): ")
    city = args.city if args.country else (input("Місто (Enter - усі міста): ") or None)

    try:
        day = WeatherQueryService.parse_date(date_text)
    except ValueError as exc:
        print(exc)
        return

    with SessionLocal() as session:
        result = WeatherQueryService(WeatherRepository(session)).search(country, day, city)

        if not result.country_known:
            print(f"Країну '{country}' не знайдено в базі. Назву вводьте англійською.")
            return
        if not result.records:
            where = f"{country}" + (f", {city}" if city else "")
            print(f"Немає даних для {where} за {day}.")
            if result.suggested_dates:
                print("Дати, за які є дані:", ", ".join(str(d) for d in result.suggested_dates), "...")
            return

        print(f"\nЗнайдено записів: {len(result.records)}")
        for record in result.records:
            print_record(record)
        print("=" * 60)


if __name__ == "__main__":
    main()
