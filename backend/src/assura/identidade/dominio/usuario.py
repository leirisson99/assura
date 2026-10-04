from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid7

from assura.identidade.dominio.email import Email
from assura.identidade.dominio.empresa import AlteracaoDeCampo
from assura.identidade.dominio.erros import NomeDeUsuarioInvalido

TAMANHO_MAXIMO_DE_NOME_DE_USUARIO = 150


class SituacaoDoUsuario(StrEnum):
    # A desativação de usuário chega na etapa 1.6.
    ATIVO = "ativo"


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

    @classmethod
    def cadastrar(cls, *, nome: str, email: Email) -> Self:
        return cls(
            id=uuid7(),
            nome=validar_nome_de_usuario(nome),
            email=email,
            situacao=SituacaoDoUsuario.ATIVO,
        )

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
