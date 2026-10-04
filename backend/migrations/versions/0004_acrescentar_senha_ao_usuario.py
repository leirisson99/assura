"""acrescentar senha ao usuario

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("usuario", sa.Column("resumo_da_senha", sa.Text(), nullable=True))
    op.add_column(
        "usuario",
        sa.Column("senha_provisoria", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "usuario",
        sa.Column(
            "administrador_do_sistema", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
    )
    op.create_check_constraint(
        op.f("ck_usuario_senha_provisoria_tem_resumo"),
        "usuario",
        "NOT senha_provisoria OR resumo_da_senha IS NOT NULL",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("ck_usuario_senha_provisoria_tem_resumo"), "usuario", type_="check")
    op.drop_column("usuario", "administrador_do_sistema")
    op.drop_column("usuario", "senha_provisoria")
    op.drop_column("usuario", "resumo_da_senha")
