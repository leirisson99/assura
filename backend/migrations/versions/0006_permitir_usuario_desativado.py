"""permitir usuario desativado

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-04
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NOME_DA_RESTRICAO = "ck_usuario_situacao_valida"


def upgrade() -> None:
    op.drop_constraint(op.f(NOME_DA_RESTRICAO), "usuario", type_="check")
    op.create_check_constraint(
        op.f(NOME_DA_RESTRICAO), "usuario", "situacao IN ('ativo', 'desativado')"
    )


def downgrade() -> None:
    # Falha se houver usuário desativado: reativá-lo aqui seria decidir por alguém.
    op.drop_constraint(op.f(NOME_DA_RESTRICAO), "usuario", type_="check")
    op.create_check_constraint(op.f(NOME_DA_RESTRICAO), "usuario", "situacao IN ('ativo')")
