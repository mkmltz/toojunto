"""persistencia de notificacoes

Revision ID: c4a8e2f6b1d3
Revises: 9b2f1c4d7e6a
Create Date: 2026-09-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4a8e2f6b1d3"
down_revision: Union[str, Sequence[str], None] = "9b2f1c4d7e6a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the notification persistence introduced by US-018."""
    op.create_table(
        "notificacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=80), nullable=False),
        sa.Column("titulo", sa.String(length=160), nullable=False),
        sa.Column("mensagem", sa.Text(), nullable=False),
        sa.Column("referencia_contextual", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("lida_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notificacoes_usuario_id"),
        "notificacoes",
        ["usuario_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove only the notification persistence introduced by US-018."""
    op.drop_index(op.f("ix_notificacoes_usuario_id"), table_name="notificacoes")
    op.drop_table("notificacoes")
