from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_vinculo
from assura.identidade.aplicacao.portas import Vinculos
from assura.identidade.dominio.vinculo import Vinculo


class DesativarVinculo:
    """Tira o acesso do usuário à empresa sem afetar o usuário nem os outros vínculos."""

    def __init__(self, vinculos: Vinculos, registrar_acao: RegistrarAcao) -> None:
        self._vinculos = vinculos
        self._registrar_acao = registrar_acao

    def executar(self, *, autor: Autor, vinculo_id: UUID) -> Vinculo:
        vinculo = self._vinculos.obter(vinculo_id)
        vinculo.desativar()
        self._vinculos.atualizar(vinculo)
        registrar_acao_sobre_vinculo(
            self._registrar_acao,
            autor=autor,
            tipo_de_acao=TipoDeAcao.VINCULO_DESATIVADO,
            vinculo=vinculo,
        )
        return vinculo


class ReativarVinculo:
    def __init__(self, vinculos: Vinculos, registrar_acao: RegistrarAcao) -> None:
        self._vinculos = vinculos
        self._registrar_acao = registrar_acao

    def executar(self, *, autor: Autor, vinculo_id: UUID) -> Vinculo:
        vinculo = self._vinculos.obter(vinculo_id)
        vinculo.reativar()
        self._vinculos.atualizar(vinculo)
        registrar_acao_sobre_vinculo(
            self._registrar_acao,
            autor=autor,
            tipo_de_acao=TipoDeAcao.VINCULO_REATIVADO,
            vinculo=vinculo,
        )
        return vinculo
