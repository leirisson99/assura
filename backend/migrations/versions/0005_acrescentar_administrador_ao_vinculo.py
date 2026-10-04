"""acrescentar administrador ao vinculo

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "vinculo",
        sa.Column(
            "administrador_da_empresa", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.create_index(
        "ix_vinculo_administradores_ativos",
        "vinculo",
        ["empresa_id"],
        postgresql_where=sa.text("administrador_da_empresa AND situacao = 'ativo'"),
    )


def downgrade() -> None:
    op.drop_index("ix_vinculo_administradores_ativos", table_name="vinculo")
    op.drop_column("vinculo", "administrador_da_empresa")
