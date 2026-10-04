from uuid import UUID

from assura.historico.aplicacao.portas import HistoricoDeAcoes, Relogio, ler_relogio_do_servidor
from assura.historico.dominio.registro_de_historico import (
    Autor,
    Detalhes,
    ObjetoAfetado,
    RegistroDeHistorico,
    TipoDeAcao,
)


class RegistrarAcao:
    """Registra uma ação na transação de quem chama, sem confirmá-la.

    A ação de negócio e o seu registro são confirmados juntos por quem abriu a transação; assim,
    se um falhar, nenhum dos dois fica gravado.
    """

    def __init__(
        self, historico: HistoricoDeAcoes, relogio: Relogio = ler_relogio_do_servidor
    ) -> None:
        self._historico = historico
        self._relogio = relogio

    def executar(
        self,
        *,
        autor: Autor,
        tipo_de_acao: TipoDeAcao,
        objeto: ObjetoAfetado,
        empresa_id: UUID | None,
        detalhes: Detalhes | None = None,
    ) -> RegistroDeHistorico:
        registro = RegistroDeHistorico.criar(
            autor=autor,
            tipo_de_acao=tipo_de_acao,
            objeto=objeto,
            empresa_id=empresa_id,
            registrado_em=self._relogio(),
            detalhes=detalhes or {},
        )
        self._historico.adicionar(registro)
        return registro
