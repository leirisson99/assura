from uuid import UUID

from assura.compartilhado.dominio.pagina import Pagina
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import (
    UsuarioAutenticado,
    UsuarioDaEmpresa,
    Usuarios,
    Vinculos,
)
from assura.identidade.dominio.usuario import Usuario
from assura.identidade.dominio.vinculo import SituacaoDoVinculo


class ConsultarUsuarios:
    def __init__(self, usuarios: Usuarios, vinculos: Vinculos, permissoes: Permissoes) -> None:
        self._usuarios = usuarios
        self._vinculos = vinculos
        self._permissoes = permissoes

    def obter(self, *, solicitante: UsuarioAutenticado, usuario_id: UUID) -> Usuario:
        usuario = self._usuarios.obter(usuario_id)
        self._permissoes.exigir_pode_ver_usuario(solicitante, usuario.id)
        return usuario

    def listar_da_empresa(
        self,
        *,
        solicitante: UsuarioAutenticado,
        empresa_id: UUID,
        situacao: SituacaoDoVinculo | None = None,
        pagina: Pagina | None = None,
    ) -> list[UsuarioDaEmpresa]:
        self._permissoes.exigir_administrador_da_empresa(solicitante, empresa_id)
        return self._vinculos.listar_da_empresa(empresa_id, situacao, pagina or Pagina())
