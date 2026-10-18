"""Шар представлення: консольна команда заповнення колонки should_go_outside.

Запуск:
    python -m app.cli.fill_go_outside
"""
import time

from app.db import SessionLocal
from app.repositories.precipitation_repository import PrecipitationRepository
from app.services.go_outside_service import GoOutsideService


def main() -> None:
    print("Заповнення колонки should_go_outside ('Чи варто виходити на вулицю')")
    started = time.time()
    with SessionLocal() as session:
        repository = PrecipitationRepository(session)
        updated = GoOutsideService(repository).fill_missing()
        stats = repository.count_by_answer()

    print(f"Готово: заповнено {updated} записів за {time.time() - started:.1f} с.")
    for answer, count in stats:
        label = {True: "так, можна виходити", False: "ні, краще вдома", None: "не заповнено"}[answer]
        print(f"  {label}: {count}")


if __name__ == "__main__":
    main()
