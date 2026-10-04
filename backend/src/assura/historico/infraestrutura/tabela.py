from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Table,
    Text,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB

from assura.compartilhado.infraestrutura.banco import metadados

tabela_registro_de_historico = Table(
    "registro_de_historico",
    metadados,
    Column("id", Uuid, primary_key=True),
    Column("autor_tipo", Text, nullable=False),
    Column("autor_usuario_id", Uuid, ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=True),
    Column("tipo_de_acao", Text, nullable=False),
    Column("objeto_tipo", Text, nullable=False),
    Column("objeto_id", Text, nullable=False),
    # Empresas nunca são excluídas; RESTRICT só protege contra exclusão acidental.
    Column("empresa_id", Uuid, ForeignKey("empresa.id", ondelete="RESTRICT"), nullable=True),
    Column("registrado_em", DateTime(timezone=True), nullable=False),
    Column("detalhes", JSONB, nullable=False, server_default=text("'{}'::jsonb")),
    CheckConstraint("autor_tipo IN ('usuario', 'sistema')", name="autor_tipo_valido"),
    CheckConstraint(
        "(autor_tipo = 'usuario') = (autor_usuario_id IS NOT NULL)",
        name="autor_usuario_coerente",
    ),
)

Index(
    "ix_registro_de_historico_empresa_registrado_em",
    tabela_registro_de_historico.c.empresa_id,
    tabela_registro_de_historico.c.registrado_em.desc(),
)
Index(
    "ix_registro_de_historico_objeto",
    tabela_registro_de_historico.c.objeto_tipo,
    tabela_registro_de_historico.c.objeto_id,
)
Index(
    "ix_registro_de_historico_autor_usuario_id",
    tabela_registro_de_historico.c.autor_usuario_id,
)
