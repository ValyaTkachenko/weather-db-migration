"""Шар представлення: перенесення даних з PostgreSQL у MySQL.

Перед запуском структуру MySQL треба створити міграціями:
    $env:DATABASE_URL="mysql+pymysql://weather:weather@localhost:3307/weather_db"
    alembic upgrade head
Запуск:
    python -m app.cli.transfer
    python -m app.cli.transfer --replace     # якщо в MySQL уже є дані
"""
import argparse
import time

from sqlalchemy import create_engine

from app.config import MYSQL_URL, POSTGRES_URL
from app.services.transfer_service import TransferService


def main() -> None:
    parser = argparse.ArgumentParser(description="Перенесення даних PostgreSQL -> MySQL")
    parser.add_argument("--replace", action="store_true", help="очистити MySQL перед перенесенням")
    args = parser.parse_args()

    service = TransferService(create_engine(POSTGRES_URL), create_engine(MYSQL_URL))

    existing = service.target_count()
    if existing and not args.replace:
        print(f"У MySQL уже є {existing} записів. Запустіть з параметром --replace.")
        return
    if args.replace:
        service.clear_target()

    print("Перенесення даних PostgreSQL -> MySQL")
    started = time.time()
    copied = service.transfer()
    print(f"Готово за {time.time() - started:.1f} с.")
    for table, count in copied.items():
        print(f"  {table}: {count} рядків")


if __name__ == "__main__":
    main()
