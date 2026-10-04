from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_vinculo
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import UsuarioAutenticado, Vinculos
from assura.identidade.dominio.erros import UltimoAdministradorNaoPodeSerRemovido
from assura.identidade.dominio.vinculo import Vinculo


def exigir_que_a_empresa_mantenha_administrador(
    vinculos: Vinculos, empresa_id: UUID, vinculo_id: UUID
) -> None:
    """Uma empresa que tem administrador não pode ficar sem nenhum (Princípio VI).

    Compara a lista, não a contagem: o vínculo pode ser de administrador com usuário desativado,
    que não está na lista e pode sair mesmo restando um só administrador ativo."""
    if vinculos.listar_administradores_ativos(empresa_id) == [vinculo_id]:
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
        exigir_que_a_empresa_mantenha_administrador(self._vinculos, vinculo.empresa_id, vinculo.id)
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
