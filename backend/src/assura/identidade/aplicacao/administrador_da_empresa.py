from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_vinculo
from assura.identidade.aplicacao.mudar_situacao_do_vinculo import (
    exigir_que_nao_seja_o_ultimo_administrador,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import UsuarioAutenticado, Vinculos
from assura.identidade.dominio.vinculo import Vinculo


class TornarAdministrador:
    def __init__(
        self, vinculos: Vinculos, permissoes: Permissoes, registrar_acao: RegistrarAcao
    ) -> None:
        self._vinculos = vinculos
        self._permissoes = permissoes
        self._registrar_acao = registrar_acao

    def executar(self, *, solicitante: UsuarioAutenticado, vinculo_id: UUID) -> Vinculo:
        vinculo = self._vinculos.obter(vinculo_id)
        self._permissoes.exigir_administrador_da_empresa(solicitante, vinculo.empresa_id)
        vinculo.tornar_administrador()
        self._vinculos.atualizar(vinculo)
        registrar_acao_sobre_vinculo(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.ADMINISTRADOR_DEFINIDO,
            vinculo=vinculo,
        )
        return vinculo


class RemoverAdministrador:
    def __init__(
        self, vinculos: Vinculos, permissoes: Permissoes, registrar_acao: RegistrarAcao
    ) -> None:
        self._vinculos = vinculos
        self._permissoes = permissoes
        self._registrar_acao = registrar_acao

    def executar(self, *, solicitante: UsuarioAutenticado, vinculo_id: UUID) -> Vinculo:
        vinculo = self._vinculos.obter(vinculo_id)
        self._permissoes.exigir_administrador_da_empresa(solicitante, vinculo.empresa_id)
        exigir_que_nao_seja_o_ultimo_administrador(self._vinculos, vinculo)
        vinculo.remover_administrador()
        self._vinculos.atualizar(vinculo)
        registrar_acao_sobre_vinculo(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.ADMINISTRADOR_REMOVIDO,
            vinculo=vinculo,
        )
        return vinculo
