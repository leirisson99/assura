"""Interface pública do contexto de histórico de ações.

Outros contextos usam apenas o que é exportado aqui, nunca a tabela diretamente.
"""

from assura.historico.aplicacao.consultar_historico import ConsultarHistorico
from assura.historico.aplicacao.portas import HistoricoDeAcoes, Relogio
from assura.historico.aplicacao.registrar_acao import RegistrarAcao
from assura.historico.dominio.consulta import FiltroDoHistorico, Pagina, SolicitanteDaConsulta
from assura.historico.dominio.erros import (
    AutorInvalido,
    ConsultaAOutraEmpresaNaoPermitida,
    ErroDoHistorico,
    ObjetoAfetadoInvalido,
    PaginaInvalida,
    PeriodoInvalido,
    TipoDeAcaoDesconhecido,
)
from assura.historico.dominio.registro_de_historico import (
    Autor,
    Detalhes,
    ObjetoAfetado,
    RegistroDeHistorico,
    TipoDeAcao,
    TipoDeAutor,
)
from assura.historico.infraestrutura.historico_sqlalchemy import criar_historico

__all__ = [
    "Autor",
    "AutorInvalido",
    "ConsultaAOutraEmpresaNaoPermitida",
    "ConsultarHistorico",
    "Detalhes",
    "ErroDoHistorico",
    "FiltroDoHistorico",
    "HistoricoDeAcoes",
    "ObjetoAfetado",
    "ObjetoAfetadoInvalido",
    "Pagina",
    "PaginaInvalida",
    "PeriodoInvalido",
    "RegistrarAcao",
    "RegistroDeHistorico",
    "Relogio",
    "SolicitanteDaConsulta",
    "TipoDeAcao",
    "TipoDeAcaoDesconhecido",
    "TipoDeAutor",
    "criar_historico",
]
