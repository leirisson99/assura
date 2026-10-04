from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid7

from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.erros import (
    EmpresaJaAtiva,
    EmpresaJaDesativada,
    NomeFantasiaInvalido,
    RazaoSocialInvalida,
)

TAMANHO_MAXIMO_DE_NOME = 150

type AlteracaoDeCampo = dict[str, str | None]


class SituacaoDaEmpresa(StrEnum):
    ATIVA = "ativa"
    DESATIVADA = "desativada"


def validar_razao_social(razao_social: str) -> str:
    razao_social = razao_social.strip()
    if not razao_social or len(razao_social) > TAMANHO_MAXIMO_DE_NOME:
        raise RazaoSocialInvalida(
            f"a razão social é obrigatória e tem até {TAMANHO_MAXIMO_DE_NOME} caracteres"
        )
    return razao_social


def validar_nome_fantasia(nome_fantasia: str | None) -> str | None:
    nome_fantasia = (nome_fantasia or "").strip()
    if len(nome_fantasia) > TAMANHO_MAXIMO_DE_NOME:
        raise NomeFantasiaInvalido(f"o nome fantasia tem até {TAMANHO_MAXIMO_DE_NOME} caracteres")
    return nome_fantasia or None


@dataclass
class Empresa:
    id: UUID
    razao_social: str
    nome_fantasia: str | None
    cnpj: Cnpj
    situacao: SituacaoDaEmpresa

    @classmethod
    def cadastrar(cls, *, razao_social: str, nome_fantasia: str | None, cnpj: Cnpj) -> Self:
        return cls(
            id=uuid7(),
            razao_social=validar_razao_social(razao_social),
            nome_fantasia=validar_nome_fantasia(nome_fantasia),
            cnpj=cnpj,
            situacao=SituacaoDaEmpresa.ATIVA,
        )

    def alterar_dados(
        self, *, razao_social: str, nome_fantasia: str | None, cnpj: Cnpj
    ) -> dict[str, AlteracaoDeCampo]:
        """Substitui os dados e devolve só os campos que mudaram, com valor anterior e novo."""
        nova_razao_social = validar_razao_social(razao_social)
        novo_nome_fantasia = validar_nome_fantasia(nome_fantasia)
        comparacoes: dict[str, tuple[str | None, str | None]] = {
            "razao_social": (self.razao_social, nova_razao_social),
            "nome_fantasia": (self.nome_fantasia, novo_nome_fantasia),
            "cnpj": (self.cnpj.valor, cnpj.valor),
        }
        self.razao_social = nova_razao_social
        self.nome_fantasia = novo_nome_fantasia
        self.cnpj = cnpj
        return {
            campo: {"anterior": anterior, "novo": novo}
            for campo, (anterior, novo) in comparacoes.items()
            if anterior != novo
        }

    def desativar(self) -> None:
        if self.situacao is SituacaoDaEmpresa.DESATIVADA:
            raise EmpresaJaDesativada(f"a empresa {self.id} já está desativada")
        self.situacao = SituacaoDaEmpresa.DESATIVADA

    def reativar(self) -> None:
        if self.situacao is SituacaoDaEmpresa.ATIVA:
            raise EmpresaJaAtiva(f"a empresa {self.id} já está ativa")
        self.situacao = SituacaoDaEmpresa.ATIVA
