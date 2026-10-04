from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid7

from assura.identidade.dominio.email import Email
from assura.identidade.dominio.empresa import AlteracaoDeCampo
from assura.identidade.dominio.erros import (
    NomeDeUsuarioInvalido,
    UsuarioJaAtivo,
    UsuarioJaDesativado,
)

TAMANHO_MAXIMO_DE_NOME_DE_USUARIO = 150


class SituacaoDoUsuario(StrEnum):
    ATIVO = "ativo"
    DESATIVADO = "desativado"


def validar_nome_de_usuario(nome: str) -> str:
    nome = nome.strip()
    if not nome or len(nome) > TAMANHO_MAXIMO_DE_NOME_DE_USUARIO:
        raise NomeDeUsuarioInvalido(
            f"o nome é obrigatório e tem até {TAMANHO_MAXIMO_DE_NOME_DE_USUARIO} caracteres"
        )
    return nome


@dataclass
class Usuario:
    id: UUID
    nome: str
    email: Email
    situacao: SituacaoDoUsuario
    # Resumo argon2id; nenhum enquanto o administrador não define a primeira senha.
    resumo_da_senha: str | None = None
    senha_provisoria: bool = False
    administrador_do_sistema: bool = False

    @classmethod
    def cadastrar(cls, *, nome: str, email: Email, administrador_do_sistema: bool = False) -> Self:
        return cls(
            id=uuid7(),
            nome=validar_nome_de_usuario(nome),
            email=email,
            situacao=SituacaoDoUsuario.ATIVO,
            administrador_do_sistema=administrador_do_sistema,
        )

    @property
    def tem_senha(self) -> bool:
        return self.resumo_da_senha is not None

    @property
    def esta_ativo(self) -> bool:
        return self.situacao is SituacaoDoUsuario.ATIVO

    def desativar(self) -> None:
        """Corta o acesso a todas as empresas; dados, senha e vínculos ficam como estão."""
        if self.situacao is SituacaoDoUsuario.DESATIVADO:
            raise UsuarioJaDesativado(f"o usuário {self.id} já está desativado")
        self.situacao = SituacaoDoUsuario.DESATIVADO

    def reativar(self) -> None:
        if self.situacao is SituacaoDoUsuario.ATIVO:
            raise UsuarioJaAtivo(f"o usuário {self.id} já está ativo")
        self.situacao = SituacaoDoUsuario.ATIVO

    def definir_senha_provisoria(self, resumo_da_senha: str) -> None:
        """Senha definida por um administrador: só permite trocar a senha até o usuário trocá-la."""
        self.resumo_da_senha = resumo_da_senha
        self.senha_provisoria = True

    def definir_senha_definitiva(self, resumo_da_senha: str) -> None:
        self.resumo_da_senha = resumo_da_senha
        self.senha_provisoria = False

    def alterar_dados(self, *, nome: str, email: Email) -> dict[str, AlteracaoDeCampo]:
        """Substitui os dados e devolve só os campos que mudaram, com valor anterior e novo."""
        novo_nome = validar_nome_de_usuario(nome)
        comparacoes = {
            "nome": (self.nome, novo_nome),
            "email": (self.email.valor, email.valor),
        }
        self.nome = novo_nome
        self.email = email
        return {
            campo: {"anterior": anterior, "novo": novo}
            for campo, (anterior, novo) in comparacoes.items()
            if anterior != novo
        }
