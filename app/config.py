"""Шар конфігурації: звідки беремо параметри підключення."""
import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://weather:weather@localhost:5432/weather_db",
)
CSV_PATH = os.getenv("CSV_PATH", "data/GlobalWeatherRepository.csv")
