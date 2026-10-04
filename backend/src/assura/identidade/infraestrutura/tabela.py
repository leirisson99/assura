from sqlalchemy import (
    CHAR,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
)

from assura.compartilhado.infraestrutura.banco import metadados

tabela_empresa = Table(
    "empresa",
    metadados,
    Column("id", Uuid, primary_key=True),
    Column("razao_social", Text, nullable=False),
    Column("nome_fantasia", Text, nullable=True),
    Column("cnpj", CHAR(14), nullable=False),
    Column("situacao", Text, nullable=False),
    UniqueConstraint("cnpj", name="uq_empresa_cnpj"),
    CheckConstraint(
        "char_length(razao_social) BETWEEN 1 AND 150", name="razao_social_tamanho_valido"
    ),
    CheckConstraint(
        "char_length(nome_fantasia) BETWEEN 1 AND 150", name="nome_fantasia_tamanho_valido"
    ),
    CheckConstraint("situacao IN ('ativa', 'desativada')", name="situacao_valida"),
)

tabela_usuario = Table(
    "usuario",
    metadados,
    Column("id", Uuid, primary_key=True),
    Column("nome", Text, nullable=False),
    Column("email", Text, nullable=False),
    Column("situacao", Text, nullable=False),
    UniqueConstraint("email", name="uq_usuario_email"),
    CheckConstraint("char_length(nome) BETWEEN 1 AND 150", name="nome_tamanho_valido"),
    CheckConstraint("email = lower(email) AND char_length(email) <= 254", name="email_normalizado"),
    CheckConstraint("situacao IN ('ativo')", name="situacao_valida"),
)

tabela_vinculo = Table(
    "vinculo",
    metadados,
    Column("id", Uuid, primary_key=True),
    Column("usuario_id", Uuid, ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
    Column("empresa_id", Uuid, ForeignKey("empresa.id", ondelete="RESTRICT"), nullable=False),
    Column("situacao", Text, nullable=False),
    UniqueConstraint("usuario_id", "empresa_id", name="uq_vinculo_usuario_empresa"),
    CheckConstraint("situacao IN ('ativo', 'desativado')", name="situacao_valida"),
)

Index("ix_vinculo_empresa_id", tabela_vinculo.c.empresa_id)
