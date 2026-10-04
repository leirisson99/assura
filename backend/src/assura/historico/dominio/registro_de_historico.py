from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Self
from uuid import UUID, uuid7

from assura.historico.dominio.erros import (
    AutorInvalido,
    ObjetoAfetadoInvalido,
    TipoDeAcaoDesconhecido,
)

type ValorJson = str | int | float | bool | None | list[ValorJson] | dict[str, ValorJson]
type Detalhes = dict[str, ValorJson]


class TipoDeAcao(StrEnum):
    """Lista fechada das ações que podem ser registradas.

    Cada funcionalidade acrescenta aqui os seus tipos, com valor no passado em snake_case
    (ex.: EMPRESA_CADASTRADA = "empresa_cadastrada").
    """

    EMPRESA_CADASTRADA = "empresa_cadastrada"
    EMPRESA_ALTERADA = "empresa_alterada"
    EMPRESA_DESATIVADA = "empresa_desativada"
    EMPRESA_REATIVADA = "empresa_reativada"
    USUARIO_CADASTRADO = "usuario_cadastrado"
    USUARIO_ALTERADO = "usuario_alterado"
    USUARIO_VINCULADO = "usuario_vinculado"
    VINCULO_DESATIVADO = "vinculo_desativado"
    VINCULO_REATIVADO = "vinculo_reativado"


class TipoDeAutor(StrEnum):
    USUARIO = "usuario"
    SISTEMA = "sistema"


@dataclass(frozen=True)
class Autor:
    tipo: TipoDeAutor
    usuario_id: UUID | None = None

    def __post_init__(self) -> None:
        autor_e_usuario = self.tipo is TipoDeAutor.USUARIO
        if autor_e_usuario != (self.usuario_id is not None):
            raise AutorInvalido("autor usuário exige identificador; autor sistema não tem")

    @classmethod
    def usuario(cls, usuario_id: UUID) -> Self:
        return cls(tipo=TipoDeAutor.USUARIO, usuario_id=usuario_id)

    @classmethod
    def sistema(cls) -> Self:
        return cls(tipo=TipoDeAutor.SISTEMA)


@dataclass(frozen=True)
class ObjetoAfetado:
    tipo: str
    identificador: str

    def __post_init__(self) -> None:
        if not self.tipo.strip() or not self.identificador.strip():
            raise ObjetoAfetadoInvalido("tipo e identificador do objeto são obrigatórios")


@dataclass(frozen=True)
class RegistroDeHistorico:
    id: UUID
    autor: Autor
    # Texto e não TipoDeAcao: registros antigos continuam legíveis mesmo que um tipo deixe de
    # existir na enumeração. A lista fechada é exigida na criação.
    tipo_de_acao: str
    objeto: ObjetoAfetado
    empresa_id: UUID | None
    registrado_em: datetime
    detalhes: Detalhes

    @classmethod
    def criar(
        cls,
        *,
        autor: Autor,
        tipo_de_acao: TipoDeAcao,
        objeto: ObjetoAfetado,
        empresa_id: UUID | None,
        registrado_em: datetime,
        detalhes: Detalhes,
    ) -> Self:
        if not isinstance(tipo_de_acao, TipoDeAcao):
            raise TipoDeAcaoDesconhecido(tipo_de_acao)
        return cls(
            id=uuid7(),
            autor=autor,
            tipo_de_acao=str(tipo_de_acao),
            objeto=objeto,
            empresa_id=empresa_id,
            registrado_em=registrado_em,
            detalhes=dict(detalhes),
        )
