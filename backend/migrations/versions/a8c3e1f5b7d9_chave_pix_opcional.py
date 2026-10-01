"""chave pix opcional

Revision ID: a8c3e1f5b7d9
Revises: f1b6c8d4a2e9
Create Date: 2026-10-01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a8c3e1f5b7d9"
down_revision: str | None = "f1b6c8d4a2e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("chave_pix", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("usuarios", "chave_pix")
