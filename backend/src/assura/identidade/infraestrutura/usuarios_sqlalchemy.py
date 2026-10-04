from typing import Any
from uuid import UUID

from sqlalchemy import Executable, RowMapping, exists, func, insert, select, update
from sqlalchemy.orm import Session

from assura.compartilhado.infraestrutura.banco import executar_traduzindo_restricoes
from assura.identidade.aplicacao.portas import Usuarios
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.erros import EmailJaCadastrado, UsuarioNaoEncontrado
from assura.identidade.dominio.usuario import SituacaoDoUsuario, Usuario
from assura.identidade.infraestrutura.tabela import tabela_usuario

colunas = tabela_usuario.c
RESTRICAO_DE_EMAIL_UNICO = "uq_usuario_email"


class UsuariosSqlAlchemy:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, usuario: Usuario) -> None:
        self._gravar(insert(tabela_usuario).values(id=usuario.id, **converter_em_colunas(usuario)))

    def atualizar(self, usuario: Usuario) -> None:
        self._gravar(
            update(tabela_usuario)
            .where(colunas.id == usuario.id)
            .values(**converter_em_colunas(usuario))
        )

    def obter(self, usuario_id: UUID) -> Usuario:
        linha = (
            self._sessao.execute(select(tabela_usuario).where(colunas.id == usuario_id))
            .mappings()
            .one_or_none()
        )
        if linha is None:
            raise UsuarioNaoEncontrado(f"usuário {usuario_id} não encontrado")
        return converter_em_usuario(linha)

    def existe_email(self, email: Email, exceto_usuario_id: UUID | None = None) -> bool:
        condicao = colunas.email == email.valor
        if exceto_usuario_id is not None:
            condicao = condicao & (colunas.id != exceto_usuario_id)
        return bool(self._sessao.scalar(select(exists().where(condicao))))

    def obter_por_email(self, email: Email) -> Usuario | None:
        linha = (
            self._sessao.execute(select(tabela_usuario).where(colunas.email == email.valor))
            .mappings()
            .one_or_none()
        )
        return None if linha is None else converter_em_usuario(linha)

    def existe_administrador_do_sistema(self) -> bool:
        return bool(
            self._sessao.scalar(select(exists().where(colunas.administrador_do_sistema.is_(True))))
        )

    def contar_administradores_do_sistema_ativos(self) -> int:
        consulta = select(func.count()).where(
            colunas.administrador_do_sistema.is_(True)
            & (colunas.situacao == str(SituacaoDoUsuario.ATIVO))
        )
        return self._sessao.scalar(consulta) or 0

    def _gravar(self, comando: Executable) -> None:
        executar_traduzindo_restricoes(
            self._sessao,
            comando,
            {
                RESTRICAO_DE_EMAIL_UNICO: lambda: EmailJaCadastrado(
                    "já existe usuário com este e-mail"
                )
            },
        )


def converter_em_colunas(usuario: Usuario) -> dict[str, Any]:
    return {
        "nome": usuario.nome,
        "email": usuario.email.valor,
        "situacao": str(usuario.situacao),
        "resumo_da_senha": usuario.resumo_da_senha,
        "senha_provisoria": usuario.senha_provisoria,
        "administrador_do_sistema": usuario.administrador_do_sistema,
    }


def converter_em_usuario(linha: RowMapping) -> Usuario:
    return Usuario(
        id=linha["id"],
        nome=linha["nome"],
        email=Email(linha["email"]),
        situacao=SituacaoDoUsuario(linha["situacao"]),
        resumo_da_senha=linha["resumo_da_senha"],
        senha_provisoria=linha["senha_provisoria"],
        administrador_do_sistema=linha["administrador_do_sistema"],
    )


def criar_usuarios(sessao: Session) -> Usuarios:
    return UsuariosSqlAlchemy(sessao)
