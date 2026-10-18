"""Шар конфігурації: звідки беремо параметри підключення."""
import os

from dotenv import load_dotenv

load_dotenv()

# Активна база, з якою працює програма і Alembic
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://weather:weather@localhost:5433/weather_db",
)
CSV_PATH = os.getenv("CSV_PATH", "data/GlobalWeatherRepository.csv")

# Етап 5: адреси обох баз для перенесення і порівняння даних
POSTGRES_URL = os.getenv(
    "POSTGRES_URL",
    "postgresql+psycopg2://weather:weather@localhost:5433/weather_db",
)
MYSQL_URL = os.getenv(
    "MYSQL_URL",
    "mysql+pymysql://weather:weather@localhost:3307/weather_db",
)
