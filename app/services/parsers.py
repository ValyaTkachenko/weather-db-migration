"""Перетворення текстових значень з CSV у типи Python."""
from datetime import datetime, time
from typing import Optional

from app.models import WindDirection

_DATETIME_FORMATS = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")
_TIME_FORMATS = ("%I:%M %p", "%H:%M", "%H:%M:%S")


def _clean(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    value = _clean(value)
    if value is None:
        return None
    for fmt in _DATETIME_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Невідомий формат дати: {value!r}")


def parse_time(value: Optional[str]) -> Optional[time]:
    """'06:04 AM' -> 06:04. Значення типу 'No sunrise' (полярний день/ніч) -> None."""
    value = _clean(value)
    if value is None or value.lower().startswith("no "):
        return None
    for fmt in _TIME_FORMATS:
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


def parse_float(value: Optional[str]) -> Optional[float]:
    value = _clean(value)
    return float(value) if value is not None else None


def parse_int(value: Optional[str]) -> Optional[int]:
    value = _clean(value)
    return int(float(value)) if value is not None else None


def parse_wind_direction(value: Optional[str]) -> Optional[WindDirection]:
    value = _clean(value)
    if value is None:
        return None
    try:
        return WindDirection(value.upper())
    except ValueError:
        return None
