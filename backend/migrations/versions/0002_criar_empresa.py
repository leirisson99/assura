"""criar empresa

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "empresa",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("razao_social", sa.Text(), nullable=False),
        sa.Column("nome_fantasia", sa.Text(), nullable=True),
        sa.Column("cnpj", sa.CHAR(14), nullable=False),
        sa.Column("situacao", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_empresa"),
        sa.UniqueConstraint("cnpj", name="uq_empresa_cnpj"),
        sa.CheckConstraint(
            "char_length(razao_social) BETWEEN 1 AND 150",
            name=op.f("ck_empresa_razao_social_tamanho_valido"),
        ),
        sa.CheckConstraint(
            "char_length(nome_fantasia) BETWEEN 1 AND 150",
            name=op.f("ck_empresa_nome_fantasia_tamanho_valido"),
        ),
        sa.CheckConstraint(
            "situacao IN ('ativa', 'desativada')", name=op.f("ck_empresa_situacao_valida")
        ),
    )
    op.create_foreign_key(
        "fk_registro_de_historico_empresa_id_empresa",
        "registro_de_historico",
        "empresa",
        ["empresa_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_registro_de_historico_empresa_id_empresa", "registro_de_historico", type_="foreignkey"
    )
    op.drop_table("empresa")
