"""criar usuario e vinculo

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "usuario",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nome", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("situacao", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_usuario"),
        sa.UniqueConstraint("email", name="uq_usuario_email"),
        sa.CheckConstraint(
            "char_length(nome) BETWEEN 1 AND 150", name=op.f("ck_usuario_nome_tamanho_valido")
        ),
        sa.CheckConstraint(
            "email = lower(email) AND char_length(email) <= 254",
            name=op.f("ck_usuario_email_normalizado"),
        ),
        sa.CheckConstraint("situacao IN ('ativo')", name=op.f("ck_usuario_situacao_valida")),
    )
    op.create_table(
        "vinculo",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=False),
        sa.Column("situacao", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_vinculo"),
        sa.ForeignKeyConstraint(
            ["usuario_id"],
            ["usuario.id"],
            name="fk_vinculo_usuario_id_usuario",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["empresa_id"],
            ["empresa.id"],
            name="fk_vinculo_empresa_id_empresa",
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("usuario_id", "empresa_id", name="uq_vinculo_usuario_empresa"),
        sa.CheckConstraint(
            "situacao IN ('ativo', 'desativado')", name=op.f("ck_vinculo_situacao_valida")
        ),
    )
    op.create_index("ix_vinculo_empresa_id", "vinculo", ["empresa_id"])
    op.create_foreign_key(
        "fk_registro_de_historico_autor_usuario_id_usuario",
        "registro_de_historico",
        "usuario",
        ["autor_usuario_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_registro_de_historico_autor_usuario_id_usuario",
        "registro_de_historico",
        type_="foreignkey",
    )
    op.drop_table("vinculo")
    op.drop_table("usuario")
