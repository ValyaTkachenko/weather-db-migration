"""ORM-модель таблиці precipitation (етап 2: дані про осади винесено окремо).

Зв'язок з weather - "один до одного": кожному запису погоди
відповідає один запис про осади.
"""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.weather import Weather


class Precipitation(Base):
    __tablename__ = "precipitation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    weather_id: Mapped[int] = mapped_column(
        ForeignKey("weather.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    precip_mm: Mapped[Optional[float]] = mapped_column(Float)   # опади, мм
    precip_in: Mapped[Optional[float]] = mapped_column(Float)   # опади, дюйми
    humidity: Mapped[Optional[int]] = mapped_column(Integer)    # вологість, %
    cloud: Mapped[Optional[int]] = mapped_column(Integer)       # хмарність, %

    weather: Mapped["Weather"] = relationship(back_populates="precipitation")

    def __repr__(self) -> str:
        return f"<Precipitation weather_id={self.weather_id} {self.precip_mm} mm>"
