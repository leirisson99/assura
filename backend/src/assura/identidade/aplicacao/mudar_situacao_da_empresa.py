from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_da_empresa import registrar_acao_sobre_empresa
from assura.identidade.aplicacao.permissoes import exigir_administrador_do_sistema
from assura.identidade.aplicacao.portas import Empresas, UsuarioAutenticado
from assura.identidade.dominio.empresa import Empresa


class DesativarEmpresa:
    def __init__(self, empresas: Empresas, registrar_acao: RegistrarAcao) -> None:
        self._empresas = empresas
        self._registrar_acao = registrar_acao

    def executar(self, *, solicitante: UsuarioAutenticado, empresa_id: UUID) -> Empresa:
        exigir_administrador_do_sistema(solicitante)
        empresa = self._empresas.obter(empresa_id)
        empresa.desativar()
        self._empresas.atualizar(empresa)
        registrar_acao_sobre_empresa(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.EMPRESA_DESATIVADA,
            empresa_id=empresa.id,
        )
        return empresa


class ReativarEmpresa:
    def __init__(self, empresas: Empresas, registrar_acao: RegistrarAcao) -> None:
        self._empresas = empresas
        self._registrar_acao = registrar_acao

    def executar(self, *, solicitante: UsuarioAutenticado, empresa_id: UUID) -> Empresa:
        exigir_administrador_do_sistema(solicitante)
        empresa = self._empresas.obter(empresa_id)
        empresa.reativar()
        self._empresas.atualizar(empresa)
        registrar_acao_sobre_empresa(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.EMPRESA_REATIVADA,
            empresa_id=empresa.id,
        )
        return empresa
