from uuid import UUID

from assura.compartilhado.dominio.pagina import Pagina
from assura.identidade.aplicacao.portas import Empresas
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa


class ConsultarEmpresas:
    def __init__(self, empresas: Empresas) -> None:
        self._empresas = empresas

    def obter(self, empresa_id: UUID) -> Empresa:
        return self._empresas.obter(empresa_id)

    def listar(
        self, *, situacao: SituacaoDaEmpresa | None = None, pagina: Pagina | None = None
    ) -> list[Empresa]:
        return self._empresas.listar(situacao, pagina or Pagina())
