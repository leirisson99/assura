from dataclasses import dataclass
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid7

from assura.identidade.dominio.erros import (
    VinculoDesativadoNaoPodeSerAdministrador,
    VinculoJaAtivo,
    VinculoJaDesativado,
    VinculoJaEAdministrador,
    VinculoNaoEAdministrador,
)


class SituacaoDoVinculo(StrEnum):
    ATIVO = "ativo"
    DESATIVADO = "desativado"


@dataclass
class Vinculo:
    """Ligação de um usuário com uma empresa; receberá setor e cargo (item 4)."""

    id: UUID
    usuario_id: UUID
    empresa_id: UUID
    situacao: SituacaoDoVinculo
    administrador_da_empresa: bool = False

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

    @property
    def e_administrador_ativo(self) -> bool:
        return self.administrador_da_empresa and self.situacao is SituacaoDoVinculo.ATIVO

    def tornar_administrador(self) -> None:
        if self.situacao is SituacaoDoVinculo.DESATIVADO:
            raise VinculoDesativadoNaoPodeSerAdministrador(
                f"o vínculo {self.id} está desativado e não pode ser administrador"
            )
        if self.administrador_da_empresa:
            raise VinculoJaEAdministrador(f"o vínculo {self.id} já é administrador da empresa")
        self.administrador_da_empresa = True

    def remover_administrador(self) -> None:
        """A regra do último administrador depende dos outros vínculos: fica no caso de uso."""
        if not self.administrador_da_empresa:
            raise VinculoNaoEAdministrador(f"o vínculo {self.id} não é administrador da empresa")
        self.administrador_da_empresa = False
