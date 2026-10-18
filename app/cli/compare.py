"""Шар представлення: порівняння баз PostgreSQL і MySQL.

Запуск:
    python -m app.cli.compare
"""
from sqlalchemy import create_engine

from app.config import MYSQL_URL, POSTGRES_URL
from app.services.transfer_service import CHECKS, run_checks


def main() -> None:
    pg = run_checks(create_engine(POSTGRES_URL))
    my = run_checks(create_engine(MYSQL_URL))

    print(f"{'Перевірка':<26}{'PostgreSQL':>22}{'MySQL':>22}   Результат")
    print("-" * 82)
    same = 0
    for (name, _), a, b in zip(CHECKS, pg, my):
        ok = str(a) == str(b)
        same += ok
        print(f"{name:<26}{str(a):>22}{str(b):>22}   {'OK' if ok else 'РІЗНИЦЯ'}")
    print("-" * 82)
    if same == len(CHECKS):
        print(f"Усі {len(CHECKS)} перевірок збіглися: бази однакові.")
    else:
        print(f"Збіглося {same} з {len(CHECKS)} перевірок.")


if __name__ == "__main__":
    main()
