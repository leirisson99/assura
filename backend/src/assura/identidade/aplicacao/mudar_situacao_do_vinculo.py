from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_vinculo
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import UsuarioAutenticado, Vinculos
from assura.identidade.dominio.erros import UltimoAdministradorNaoPodeSerRemovido
from assura.identidade.dominio.vinculo import Vinculo


def exigir_que_nao_seja_o_ultimo_administrador(vinculos: Vinculos, vinculo: Vinculo) -> None:
    """Uma empresa que tem administrador não pode ficar sem nenhum (Princípio V)."""
    if not vinculo.e_administrador_ativo:
        return
    if vinculos.contar_administradores_ativos(vinculo.empresa_id) <= 1:
        raise UltimoAdministradorNaoPodeSerRemovido(
            "a empresa precisa de ao menos um administrador; defina outro antes"
        )


class DesativarVinculo:
    """Tira o acesso do usuário à empresa sem afetar o usuário nem os outros vínculos."""

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
        vinculo.desativar()
        self._vinculos.atualizar(vinculo)
        registrar_acao_sobre_vinculo(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.VINCULO_DESATIVADO,
            vinculo=vinculo,
        )
        return vinculo


class ReativarVinculo:
    def __init__(
        self, vinculos: Vinculos, permissoes: Permissoes, registrar_acao: RegistrarAcao
    ) -> None:
        self._vinculos = vinculos
        self._permissoes = permissoes
        self._registrar_acao = registrar_acao

    def executar(self, *, solicitante: UsuarioAutenticado, vinculo_id: UUID) -> Vinculo:
        vinculo = self._vinculos.obter(vinculo_id)
        self._permissoes.exigir_administrador_da_empresa(solicitante, vinculo.empresa_id)
        vinculo.reativar()
        self._vinculos.atualizar(vinculo)
        registrar_acao_sobre_vinculo(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.VINCULO_REATIVADO,
            vinculo=vinculo,
        )
        return vinculo
