from sqlalchemy import (
    CHAR,
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    false,
    text,
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
    Column("resumo_da_senha", Text, nullable=True),
    Column("senha_provisoria", Boolean, nullable=False, server_default=false()),
    Column("administrador_do_sistema", Boolean, nullable=False, server_default=false()),
    UniqueConstraint("email", name="uq_usuario_email"),
    CheckConstraint(
        "NOT senha_provisoria OR resumo_da_senha IS NOT NULL", name="senha_provisoria_tem_resumo"
    ),
    CheckConstraint("char_length(nome) BETWEEN 1 AND 150", name="nome_tamanho_valido"),
    CheckConstraint("email = lower(email) AND char_length(email) <= 254", name="email_normalizado"),
    CheckConstraint("situacao IN ('ativo', 'desativado')", name="situacao_valida"),
)

tabela_vinculo = Table(
    "vinculo",
    metadados,
    Column("id", Uuid, primary_key=True),
    Column("usuario_id", Uuid, ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
    Column("empresa_id", Uuid, ForeignKey("empresa.id", ondelete="RESTRICT"), nullable=False),
    Column("situacao", Text, nullable=False),
    Column("administrador_da_empresa", Boolean, nullable=False, server_default=false()),
    UniqueConstraint("usuario_id", "empresa_id", name="uq_vinculo_usuario_empresa"),
    CheckConstraint("situacao IN ('ativo', 'desativado')", name="situacao_valida"),
)

Index("ix_vinculo_empresa_id", tabela_vinculo.c.empresa_id)
Index(
    "ix_vinculo_administradores_ativos",
    tabela_vinculo.c.empresa_id,
    postgresql_where=text("administrador_da_empresa AND situacao = 'ativo'"),
)
