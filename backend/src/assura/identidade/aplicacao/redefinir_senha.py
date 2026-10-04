from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_usuario
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import (
    GeradorDeResumoDeSenha,
    UsuarioAutenticado,
    Usuarios,
)
from assura.identidade.dominio.senha import validar_senha


class RedefinirSenha:
    """Define uma senha provisória; o usuário só consegue trocá-la até escolher a dele."""

    def __init__(
        self,
        usuarios: Usuarios,
        permissoes: Permissoes,
        gerador_de_resumo: GeradorDeResumoDeSenha,
        registrar_acao: RegistrarAcao,
    ) -> None:
        self._usuarios = usuarios
        self._permissoes = permissoes
        self._gerador_de_resumo = gerador_de_resumo
        self._registrar_acao = registrar_acao

    def executar(
        self, *, solicitante: UsuarioAutenticado, usuario_id: UUID, senha_provisoria: str
    ) -> None:
        usuario = self._usuarios.obter(usuario_id)
        self._permissoes.exigir_pode_redefinir_senha(solicitante, usuario)
        resumo = self._gerador_de_resumo.gerar(validar_senha(senha_provisoria))
        usuario.definir_senha_provisoria(resumo)
        self._usuarios.atualizar(usuario)
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.SENHA_REDEFINIDA,
            usuario_id=usuario.id,
        )
