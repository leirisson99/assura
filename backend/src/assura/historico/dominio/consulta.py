from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Self
from uuid import UUID

from assura.historico.dominio.erros import (
    ConsultaAOutraEmpresaNaoPermitida,
    PeriodoInvalido,
)
from assura.historico.dominio.registro_de_historico import Autor, ObjetoAfetado, TipoDeAcao


class AlcanceDaConsulta(StrEnum):
    TODAS_AS_EMPRESAS = "todas_as_empresas"
    UMA_EMPRESA = "uma_empresa"


@dataclass(frozen=True)
class FiltroDoHistorico:
    empresa_id: UUID | None = None
    inicio: datetime | None = None
    fim: datetime | None = None
    autor: Autor | None = None
    tipo_de_acao: TipoDeAcao | None = None
    objeto: ObjetoAfetado | None = None

    def __post_init__(self) -> None:
        if self.inicio is not None and self.fim is not None and self.inicio > self.fim:
            raise PeriodoInvalido("o início do período não pode ser depois do fim")


@dataclass(frozen=True)
class SolicitanteDaConsulta:
    alcance: AlcanceDaConsulta
    empresa_id: UUID | None = None

    @classmethod
    def administrador_do_sistema(cls) -> Self:
        return cls(alcance=AlcanceDaConsulta.TODAS_AS_EMPRESAS)

    @classmethod
    def administrador_da_empresa(cls, empresa_id: UUID) -> Self:
        return cls(alcance=AlcanceDaConsulta.UMA_EMPRESA, empresa_id=empresa_id)

    def definir_empresa_da_consulta(self, empresa_pedida: UUID | None) -> UUID | None:
        """Devolve a empresa a que a consulta fica restrita; nenhuma significa todas."""
        if self.alcance is AlcanceDaConsulta.TODAS_AS_EMPRESAS:
            return empresa_pedida
        if empresa_pedida is not None and empresa_pedida != self.empresa_id:
            raise ConsultaAOutraEmpresaNaoPermitida(
                "administrador da empresa só consulta o histórico da própria empresa"
            )
        return self.empresa_id
