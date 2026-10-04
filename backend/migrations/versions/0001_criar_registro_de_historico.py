"""criar registro_de_historico

Revision ID: 0001
Revises:
Create Date: 2026-10-04
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

MENSAGEM_DE_HISTORICO_IMUTAVEL = "o histórico de ações não pode ser alterado nem excluído"


def upgrade() -> None:
    op.create_table(
        "registro_de_historico",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("autor_tipo", sa.Text(), nullable=False),
        sa.Column("autor_usuario_id", sa.Uuid(), nullable=True),
        sa.Column("tipo_de_acao", sa.Text(), nullable=False),
        sa.Column("objeto_tipo", sa.Text(), nullable=False),
        sa.Column("objeto_id", sa.Text(), nullable=False),
        sa.Column("empresa_id", sa.Uuid(), nullable=True),
        sa.Column("registrado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "detalhes",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.CheckConstraint(
            "autor_tipo IN ('usuario', 'sistema')",
            name=op.f("ck_registro_de_historico_autor_tipo_valido"),
        ),
        sa.CheckConstraint(
            "(autor_tipo = 'usuario') = (autor_usuario_id IS NOT NULL)",
            name=op.f("ck_registro_de_historico_autor_usuario_coerente"),
        ),
        sa.PrimaryKeyConstraint("id", name="pk_registro_de_historico"),
    )
    op.create_index(
        "ix_registro_de_historico_empresa_registrado_em",
        "registro_de_historico",
        ["empresa_id", sa.text("registrado_em DESC")],
    )
    op.create_index(
        "ix_registro_de_historico_objeto",
        "registro_de_historico",
        ["objeto_tipo", "objeto_id"],
    )
    op.create_index(
        "ix_registro_de_historico_autor_usuario_id",
        "registro_de_historico",
        ["autor_usuario_id"],
    )
    op.execute(
        f"""
        CREATE FUNCTION impedir_alteracao_do_historico() RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION '{MENSAGEM_DE_HISTORICO_IMUTAVEL}';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER registro_de_historico_impedir_alteracao
        BEFORE UPDATE OR DELETE ON registro_de_historico
        FOR EACH ROW EXECUTE FUNCTION impedir_alteracao_do_historico()
        """
    )
    op.execute(
        """
        CREATE TRIGGER registro_de_historico_impedir_truncate
        BEFORE TRUNCATE ON registro_de_historico
        FOR EACH STATEMENT EXECUTE FUNCTION impedir_alteracao_do_historico()
        """
    )


def downgrade() -> None:
    op.drop_table("registro_de_historico")
    op.execute("DROP FUNCTION impedir_alteracao_do_historico()")
