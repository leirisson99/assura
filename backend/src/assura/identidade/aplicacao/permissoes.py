from uuid import UUID

from assura.identidade.aplicacao.portas import Empresas, UsuarioAutenticado, Vinculos
from assura.identidade.dominio.empresa import SituacaoDaEmpresa
from assura.identidade.dominio.erros import PermissaoNegada
from assura.identidade.dominio.usuario import Usuario


def exigir_administrador_do_sistema(solicitante: UsuarioAutenticado) -> None:
    if not solicitante.administrador_do_sistema:
        raise PermissaoNegada("ação exclusiva do administrador do sistema")


class Permissoes:
    """Quem pode o quê na etapa 1 (Princípio V: papéis fixos, nada configurável)."""

    def __init__(self, vinculos: Vinculos, empresas: Empresas) -> None:
        self._vinculos = vinculos
        self._empresas = empresas

    def exigir_administrador_do_sistema(self, solicitante: UsuarioAutenticado) -> None:
        exigir_administrador_do_sistema(solicitante)

    def e_administrador_da_empresa(self, solicitante: UsuarioAutenticado, empresa_id: UUID) -> bool:
        """O administrador do sistema administra qualquer empresa. Os demais precisam de vínculo
        ativo, marcado como administrador, com empresa ativa."""
        if solicitante.administrador_do_sistema:
            return True
        vinculo = self._vinculos.obter_do_usuario_na_empresa(solicitante.id, empresa_id)
        if vinculo is None or not vinculo.e_administrador_ativo:
            return False
        return self._empresas.obter(empresa_id).situacao is SituacaoDaEmpresa.ATIVA

    def exigir_administrador_da_empresa(
        self, solicitante: UsuarioAutenticado, empresa_id: UUID
    ) -> None:
        if not self.e_administrador_da_empresa(solicitante, empresa_id):
            raise PermissaoNegada("ação exclusiva dos administradores desta empresa")

    def exigir_pode_ver_usuario(self, solicitante: UsuarioAutenticado, usuario_id: UUID) -> None:
        if solicitante.id == usuario_id or solicitante.administrador_do_sistema:
            return
        empresas_do_usuario = {
            vinculo.empresa_id for vinculo in self._vinculos.listar_ativos_do_usuario(usuario_id)
        }
        if not any(
            self.e_administrador_da_empresa(solicitante, empresa_id)
            for empresa_id in empresas_do_usuario
        ):
            raise PermissaoNegada("usuário fora das empresas que você administra")

    def exigir_pode_redefinir_senha(self, solicitante: UsuarioAutenticado, alvo: Usuario) -> None:
        """O administrador da empresa só redefine a senha de quem trabalha apenas em empresas que
        ele administra: senão entraria nas outras empresas como essa pessoa."""
        if solicitante.administrador_do_sistema:
            return
        if alvo.administrador_do_sistema:
            raise PermissaoNegada("só o administrador do sistema redefine a senha de outro")
        empresas_do_alvo = {
            vinculo.empresa_id for vinculo in self._vinculos.listar_ativos_do_usuario(alvo.id)
        }
        administra_todas = bool(empresas_do_alvo) and all(
            self.e_administrador_da_empresa(solicitante, empresa_id)
            for empresa_id in empresas_do_alvo
        )
        if not administra_todas:
            raise PermissaoNegada(
                "o usuário tem vínculo com empresa que você não administra; "
                "peça ao administrador do sistema"
            )
