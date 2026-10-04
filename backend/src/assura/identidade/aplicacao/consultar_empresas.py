from uuid import UUID

from assura.compartilhado.dominio.pagina import Pagina
from assura.identidade.aplicacao.permissoes import Permissoes, exigir_administrador_do_sistema
from assura.identidade.aplicacao.portas import Empresas, UsuarioAutenticado
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa


class ConsultarEmpresas:
    def __init__(self, empresas: Empresas, permissoes: Permissoes) -> None:
        self._empresas = empresas
        self._permissoes = permissoes

    def obter(self, *, solicitante: UsuarioAutenticado, empresa_id: UUID) -> Empresa:
        empresa = self._empresas.obter(empresa_id)
        self._permissoes.exigir_administrador_da_empresa(solicitante, empresa.id)
        return empresa

    def listar(
        self,
        *,
        solicitante: UsuarioAutenticado,
        situacao: SituacaoDaEmpresa | None = None,
        pagina: Pagina | None = None,
    ) -> list[Empresa]:
        exigir_administrador_do_sistema(solicitante)
        return self._empresas.listar(situacao, pagina or Pagina())
