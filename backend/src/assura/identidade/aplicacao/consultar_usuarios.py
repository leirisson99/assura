from uuid import UUID

from assura.compartilhado.dominio.pagina import Pagina
from assura.identidade.aplicacao.portas import UsuarioDaEmpresa, Usuarios, Vinculos
from assura.identidade.dominio.usuario import Usuario
from assura.identidade.dominio.vinculo import SituacaoDoVinculo


class ConsultarUsuarios:
    def __init__(self, usuarios: Usuarios, vinculos: Vinculos) -> None:
        self._usuarios = usuarios
        self._vinculos = vinculos

    def obter(self, usuario_id: UUID) -> Usuario:
        return self._usuarios.obter(usuario_id)

    def listar_da_empresa(
        self,
        empresa_id: UUID,
        *,
        situacao: SituacaoDoVinculo | None = None,
        pagina: Pagina | None = None,
    ) -> list[UsuarioDaEmpresa]:
        return self._vinculos.listar_da_empresa(empresa_id, situacao, pagina or Pagina())
