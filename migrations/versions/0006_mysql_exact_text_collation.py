"""MySQL: точне порівняння тексту (collation utf8mb4_bin), як у PostgreSQL

Проблема, виявлена при порівнянні баз після перенесення даних:
  у датасеті є назви "Turkmenistan" і "Turkménistan".
  - PostgreSQL порівнює текст точно, тому це дві різні назви (211 країн);
  - MySQL за замовчуванням використовує utf8mb4_0900_ai_ci
    (ai - без урахування діакритики, ci - без урахування регістру),
    тому вважає їх однаковими (210 країн).
Отже, однакові запити (DISTINCT, GROUP BY, =) давали різні результати.
Для MySQL задаємо collation utf8mb4_bin - точне порівняння, як у PostgreSQL.
У PostgreSQL міграція нічого не змінює.

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-18
"""
from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def _set_collation(collation: str) -> None:
    if op.get_bind().dialect.name != "mysql":
        return  # PostgreSQL та інші СУБД: змін не потрібно
    op.execute(
        f"""
        ALTER TABLE weather
            MODIFY country        VARCHAR(100) COLLATE {collation} NOT NULL,
            MODIFY location_name  VARCHAR(255) COLLATE {collation} NOT NULL,
            MODIFY condition_text VARCHAR(100) COLLATE {collation} NULL
        """
    )


def upgrade() -> None:
    _set_collation("utf8mb4_bin")


def downgrade() -> None:
    _set_collation("utf8mb4_0900_ai_ci")
