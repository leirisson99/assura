from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid7

from assura.identidade.dominio.erros import VinculoJaAtivo, VinculoJaDesativado


class SituacaoDoVinculo(StrEnum):
    ATIVO = "ativo"
    DESATIVADO = "desativado"


@dataclass
class Vinculo:
    """Ligação de um usuário com uma empresa; receberá setor, cargo e papel."""

    id: UUID
    usuario_id: UUID
    empresa_id: UUID
    situacao: SituacaoDoVinculo

    @classmethod
    def criar(cls, *, usuario_id: UUID, empresa_id: UUID) -> Self:
        return cls(
            id=uuid7(),
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            situacao=SituacaoDoVinculo.ATIVO,
        )

    def desativar(self) -> None:
        if self.situacao is SituacaoDoVinculo.DESATIVADO:
            raise VinculoJaDesativado(f"o vínculo {self.id} já está desativado")
        self.situacao = SituacaoDoVinculo.DESATIVADO

    def reativar(self) -> None:
        if self.situacao is SituacaoDoVinculo.ATIVO:
            raise VinculoJaAtivo(f"o vínculo {self.id} já está ativo")
        self.situacao = SituacaoDoVinculo.ATIVO
