# Міграція погодної бази даних

Лабораторна робота. Варіант 19 → категорія **осади** (19 mod 4 = 3).

Стек: Python, SQLAlchemy (ORM), Alembic (міграції), PostgreSQL, MySQL, Docker.

## Архітектура (Layered Architecture)

```
app/
  config.py        – налаштування (URL бази, шлях до CSV)
  db.py            – підключення до БД
  models/          – шар моделей (ORM-опис таблиць)
  repositories/    – шар доступу до даних (запити до БД)
  services/        – шар бізнес-логіки (імпорт CSV, формула "чи виходити")
  cli/             – шар представлення (консольний інтерфейс)
migrations/        – міграції Alembic
data/              – сюди кладеться CSV з Kaggle
```

## Запуск

```powershell
docker compose up -d
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
```
