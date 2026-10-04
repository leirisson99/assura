class ErroDoHistorico(Exception):
    """Base dos erros de negócio do histórico de ações."""


class TipoDeAcaoDesconhecido(ErroDoHistorico):
    def __init__(self, tipo_de_acao: object) -> None:
        super().__init__(f"tipo de ação fora da lista de tipos conhecidos: {tipo_de_acao!r}")


class AutorInvalido(ErroDoHistorico):
    pass


class ObjetoAfetadoInvalido(ErroDoHistorico):
    pass


class PeriodoInvalido(ErroDoHistorico):
    pass


class PaginaInvalida(ErroDoHistorico):
    pass


class ConsultaAOutraEmpresaNaoPermitida(ErroDoHistorico):
    pass
