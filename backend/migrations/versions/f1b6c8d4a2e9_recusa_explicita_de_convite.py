"""recusa explicita de convite

Revision ID: f1b6c8d4a2e9
Revises: e7d3a9c5f2b4
Create Date: 2026-09-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1b6c8d4a2e9"
down_revision: Union[str, Sequence[str], None] = "e7d3a9c5f2b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Persist one explicit rejection per invite and authenticated user."""
    op.create_table(
        "recusas_convite",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("convite_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["convite_id"], ["convites.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "convite_id",
            "usuario_id",
            name="uq_recusas_convite_convite_usuario",
        ),
    )
    op.create_index(
        op.f("ix_recusas_convite_convite_id"),
        "recusas_convite",
        ["convite_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_recusas_convite_usuario_id"),
        "recusas_convite",
        ["usuario_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove only explicit invite rejection persistence."""
    op.drop_index(
        op.f("ix_recusas_convite_usuario_id"),
        table_name="recusas_convite",
    )
    op.drop_index(
        op.f("ix_recusas_convite_convite_id"),
        table_name="recusas_convite",
    )
    op.drop_table("recusas_convite")
