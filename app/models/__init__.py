"""Шар моделей (ORM). Тут описана структура таблиць."""
from app.models.base import Base
from app.models.precipitation import Precipitation
from app.models.weather import Weather, WindDirection

__all__ = ["Base", "Weather", "WindDirection", "Precipitation"]
