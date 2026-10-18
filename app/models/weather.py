"""ORM-модель таблиці weather.

Етап 2: колонки категорії "осади" винесено в окрему таблицю precipitation
(див. app/models/precipitation.py). Тут залишилися загальні дані про погоду.
"""
import enum
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Enum, Float, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.precipitation import Precipitation


class WindDirection(str, enum.Enum):
    """16 румбів напрямку вітру, як у датасеті."""

    N = "N"
    NNE = "NNE"
    NE = "NE"
    ENE = "ENE"
    E = "E"
    ESE = "ESE"
    SE = "SE"
    SSE = "SSE"
    S = "S"
    SSW = "SSW"
    SW = "SW"
    WSW = "WSW"
    W = "W"
    WNW = "WNW"
    NW = "NW"
    NNW = "NNW"


class Weather(Base):
    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # --- обов'язкові типи колонок ---
    country: Mapped[str] = mapped_column(String(100), index=True)          # текст
    location_name: Mapped[str] = mapped_column(String(255))                # текст
    last_updated: Mapped[datetime] = mapped_column(DateTime, index=True)   # дата
    wind_degree: Mapped[Optional[int]] = mapped_column(Integer)            # ціле
    wind_kph: Mapped[Optional[float]] = mapped_column(Float)               # дробне
    wind_direction: Mapped[Optional[WindDirection]] = mapped_column(       # enum
        Enum(WindDirection, name="wind_direction_enum")
    )
    sunrise: Mapped[Optional[time]] = mapped_column(Time)                  # час

    # --- загальна інформація для виводу ---
    temperature_celsius: Mapped[Optional[float]] = mapped_column(Float)
    condition_text: Mapped[Optional[str]] = mapped_column(String(100))

    # --- зв'язок "один до одного" з таблицею осадів ---
    precipitation: Mapped[Optional["Precipitation"]] = relationship(
        back_populates="weather", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Weather {self.country} {self.location_name} {self.last_updated}>"
