"""confiabilidade do email

Revision ID: e7d3a9c5f2b4
Revises: c4a8e2f6b1d3
Create Date: 2026-09-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e7d3a9c5f2b4"
down_revision: Union[str, Sequence[str], None] = "c4a8e2f6b1d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create email delivery result persistence introduced by US-023."""
    op.create_table(
        "entregas_email",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("notificacao_id", sa.Integer(), nullable=True),
        sa.Column("destinatario", sa.String(length=255), nullable=False),
        sa.Column("evento", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("tentativas", sa.Integer(), nullable=False),
        sa.Column("tentado_em", sa.DateTime(), nullable=False),
        sa.Column("enviado_em", sa.DateTime(), nullable=True),
        sa.Column("erro", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["notificacao_id"], ["notificacoes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_entregas_email_notificacao_id"),
        "entregas_email",
        ["notificacao_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove only the email delivery persistence introduced by US-023."""
    op.drop_index(
        op.f("ix_entregas_email_notificacao_id"),
        table_name="entregas_email",
    )
    op.drop_table("entregas_email")
