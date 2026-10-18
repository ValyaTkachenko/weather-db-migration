"""Шар бізнес-логіки: відповідь на питання "Чи варто виходити на вулицю?".

Формула (категорія "осади"):
    НЕ виходити, якщо
        - опадів 1 мм і більше, АБО
        - вологість >= 90 % і водночас хмарність >= 80 % (сиро й похмуро);
    в інших випадках - виходити можна.
"""
from typing import Optional

from app.repositories.precipitation_repository import PrecipitationRepository

PRECIP_LIMIT_MM = 1.0
HUMIDITY_LIMIT = 90
CLOUD_LIMIT = 80


def should_go_outside(
    precip_mm: Optional[float], humidity: Optional[int], cloud: Optional[int]
) -> bool:
    """Формула. Відсутні значення вважаються нулями."""
    precip_mm = precip_mm or 0.0
    humidity = humidity or 0
    cloud = cloud or 0

    if precip_mm >= PRECIP_LIMIT_MM:
        return False
    if humidity >= HUMIDITY_LIMIT and cloud >= CLOUD_LIMIT:
        return False
    return True


class GoOutsideService:
    def __init__(self, repository: PrecipitationRepository):
        self.repository = repository

    def fill_missing(self, batch_size: int = 5000) -> int:
        """Заповнює колонку для всіх записів, де вона ще порожня (NULL)."""
        updated = 0
        while True:
            rows = self.repository.get_unfilled(batch_size)
            if not rows:
                break
            values = [
                {
                    "id": row.id,
                    "should_go_outside": should_go_outside(
                        row.precip_mm, row.humidity, row.cloud
                    ),
                }
                for row in rows
            ]
            self.repository.bulk_update_go_outside(values)
            self.repository.session.commit()
            updated += len(values)
            print(f"  заповнено {updated} записів...")
        return updated
