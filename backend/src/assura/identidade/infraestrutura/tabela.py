from sqlalchemy import CHAR, CheckConstraint, Column, Table, Text, UniqueConstraint, Uuid

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
