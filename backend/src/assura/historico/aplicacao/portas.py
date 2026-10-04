from collections.abc import Callable
from datetime import UTC, datetime
from typing import Protocol

from assura.historico.dominio.consulta import FiltroDoHistorico, Pagina
from assura.historico.dominio.registro_de_historico import RegistroDeHistorico

type Relogio = Callable[[], datetime]


def ler_relogio_do_servidor() -> datetime:
    return datetime.now(UTC)


class HistoricoDeAcoes(Protocol):
    """Armazenamento só de inserção: não existe operação de alterar nem de excluir."""

    def adicionar(self, registro: RegistroDeHistorico) -> None: ...

    def consultar(self, filtro: FiltroDoHistorico, pagina: Pagina) -> list[RegistroDeHistorico]:
        """Filtro já restrito à empresa permitida; resultado do mais recente ao mais antigo."""
        ...
