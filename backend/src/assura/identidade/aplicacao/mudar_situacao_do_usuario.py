from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_usuario
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import Empresas, UsuarioAutenticado, Usuarios, Vinculos
from assura.identidade.dominio.erros import (
    UltimoAdministradorDoSistemaNaoPodeSerDesativado,
    UltimoAdministradorNaoPodeSerRemovido,
)
from assura.identidade.dominio.usuario import Usuario


class DesativarUsuario:
    """Tira o acesso da pessoa a todas as empresas de uma vez, sem excluir nada (Princípio IV)."""

    def __init__(
        self,
        usuarios: Usuarios,
        vinculos: Vinculos,
        empresas: Empresas,
        permissoes: Permissoes,
        registrar_acao: RegistrarAcao,
    ) -> None:
        self._usuarios = usuarios
        self._vinculos = vinculos
        self._empresas = empresas
        self._permissoes = permissoes
        self._registrar_acao = registrar_acao

    def executar(self, *, solicitante: UsuarioAutenticado, usuario_id: UUID) -> Usuario:
        self._permissoes.exigir_administrador_do_sistema(solicitante)
        usuario = self._usuarios.obter(usuario_id)
        usuario.desativar()
        self._exigir_que_o_sistema_mantenha_administrador(usuario)
        self._exigir_que_as_empresas_mantenham_administrador(usuario)
        self._usuarios.atualizar(usuario)
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.USUARIO_DESATIVADO,
            usuario_id=usuario.id,
        )
        return usuario

    def _exigir_que_o_sistema_mantenha_administrador(self, usuario: Usuario) -> None:
        # Hoje só existe o root e não há como criar outro, por isso não há bloqueio de linhas.
        if not usuario.administrador_do_sistema:
            return
        if self._usuarios.contar_administradores_do_sistema_ativos() <= 1:
            raise UltimoAdministradorDoSistemaNaoPodeSerDesativado(
                "o sistema precisa de ao menos um administrador do sistema ativo"
            )

    def _exigir_que_as_empresas_mantenham_administrador(self, usuario: Usuario) -> None:
        # Ordem de empresa fixa: duas desativações simultâneas bloqueiam na mesma ordem.
        vinculos_administradores = sorted(
            (
                vinculo
                for vinculo in self._vinculos.listar_ativos_do_usuario(usuario.id)
                if vinculo.administrador_da_empresa
            ),
            key=lambda vinculo: vinculo.empresa_id,
        )
        for vinculo in vinculos_administradores:
            if self._vinculos.listar_administradores_ativos(vinculo.empresa_id) == [vinculo.id]:
                empresa = self._empresas.obter(vinculo.empresa_id)
                raise UltimoAdministradorNaoPodeSerRemovido(
                    f"o usuário é o único administrador ativo da empresa {empresa.razao_social}; "
                    "defina outro antes"
                )


class ReativarUsuario:
    """Devolve o acesso com a mesma senha, os mesmos vínculos e os mesmos papéis."""

    def __init__(
        self, usuarios: Usuarios, permissoes: Permissoes, registrar_acao: RegistrarAcao
    ) -> None:
        self._usuarios = usuarios
        self._permissoes = permissoes
        self._registrar_acao = registrar_acao

    def executar(self, *, solicitante: UsuarioAutenticado, usuario_id: UUID) -> Usuario:
        self._permissoes.exigir_administrador_do_sistema(solicitante)
        usuario = self._usuarios.obter(usuario_id)
        usuario.reativar()
        self._usuarios.atualizar(usuario)
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.USUARIO_REATIVADO,
            usuario_id=usuario.id,
        )
        return usuario
