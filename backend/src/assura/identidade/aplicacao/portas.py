from typing import Protocol
from uuid import UUID

from assura.compartilhado.dominio.pagina import Pagina
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa


class Empresas(Protocol):
    """Armazenamento de empresas: não existe operação de excluir (Princípio III)."""

    def adicionar(self, empresa: Empresa) -> None:
        """Recusa CNPJ repetido com CnpjJaCadastrado, mesmo em gravações simultâneas."""
        ...

    def atualizar(self, empresa: Empresa) -> None:
        """Recusa CNPJ repetido com CnpjJaCadastrado, mesmo em gravações simultâneas."""
        ...

    def obter(self, empresa_id: UUID) -> Empresa:
        """Recusa identificador inexistente com EmpresaNaoEncontrada."""
        ...

    def existe_cnpj(self, cnpj: Cnpj, exceto_empresa_id: UUID | None = None) -> bool: ...

    def listar(self, situacao: SituacaoDaEmpresa | None, pagina: Pagina) -> list[Empresa]:
        """Ordem alfabética de razão social; situação nenhuma lista todas."""
        ...
