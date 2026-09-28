"""baseline MVP 0.1

Revision ID: 9b2f1c4d7e6a
Revises:
Create Date: 2026-09-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b2f1c4d7e6a"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the complete schema homologated for MVP 0.1."""
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("telefone", sa.String(length=30), nullable=True),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_usuarios_email"), "usuarios", ["email"], unique=True)

    op.create_table(
        "grupos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("gestor_id", sa.Integer(), nullable=False),
        sa.Column("valor_cota", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("valor_premio", sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column("quantidade_participantes", sa.Integer(), nullable=False),
        sa.Column("quantidade_ciclos", sa.Integer(), nullable=False),
        sa.Column("data_inicio", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["gestor_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "convites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("grupo_id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["grupo_id"], ["grupos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_convites_grupo_id"), "convites", ["grupo_id"], unique=True)
    op.create_index(op.f("ix_convites_token"), "convites", ["token"], unique=True)

    op.create_table(
        "participantes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("grupo_id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("ordem_sorteio", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["grupo_id"], ["grupos.id"]),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ciclos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("grupo_id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("data", sa.DateTime(), nullable=True),
        sa.Column("contemplado_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["contemplado_id"], ["participantes.id"]),
        sa.ForeignKeyConstraint(["grupo_id"], ["grupos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "contemplacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ciclo_id", sa.Integer(), nullable=False),
        sa.Column("participante_id", sa.Integer(), nullable=False),
        sa.Column("valor", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("data", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ciclo_id"], ["ciclos.id"]),
        sa.ForeignKeyConstraint(["participante_id"], ["participantes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "pagamentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ciclo_id", sa.Integer(), nullable=False),
        sa.Column("pagador_id", sa.Integer(), nullable=False),
        sa.Column("recebedor_id", sa.Integer(), nullable=False),
        sa.Column("valor", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("comprovante", sa.Text(), nullable=True),
        sa.Column("data_pagamento", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ciclo_id"], ["ciclos.id"]),
        sa.ForeignKeyConstraint(["pagador_id"], ["participantes.id"]),
        sa.ForeignKeyConstraint(["recebedor_id"], ["participantes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove only the objects introduced by the MVP 0.1 baseline."""
    op.drop_table("pagamentos")
    op.drop_table("contemplacoes")
    op.drop_table("ciclos")
    op.drop_table("participantes")
    op.drop_index(op.f("ix_convites_token"), table_name="convites")
    op.drop_index(op.f("ix_convites_grupo_id"), table_name="convites")
    op.drop_table("convites")
    op.drop_table("grupos")
    op.drop_index(op.f("ix_usuarios_email"), table_name="usuarios")
    op.drop_table("usuarios")
