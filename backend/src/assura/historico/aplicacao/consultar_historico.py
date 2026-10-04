from dataclasses import replace

from assura.compartilhado.dominio.pagina import Pagina
from assura.historico.aplicacao.portas import HistoricoDeAcoes
from assura.historico.dominio.consulta import FiltroDoHistorico, SolicitanteDaConsulta
from assura.historico.dominio.registro_de_historico import RegistroDeHistorico


class ConsultarHistorico:
    def __init__(self, historico: HistoricoDeAcoes) -> None:
        self._historico = historico

    def executar(
        self,
        *,
        solicitante: SolicitanteDaConsulta,
        filtro: FiltroDoHistorico,
        pagina: Pagina,
    ) -> list[RegistroDeHistorico]:
        empresa_da_consulta = solicitante.definir_empresa_da_consulta(filtro.empresa_id)
        filtro_restrito = replace(filtro, empresa_id=empresa_da_consulta)
        return self._historico.consultar(filtro_restrito, pagina)
