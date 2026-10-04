from uuid import UUID

from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_usuario
from assura.identidade.aplicacao.portas import (
    GeradorDeResumoDeSenha,
    UsuarioAutenticado,
    Usuarios,
)
from assura.identidade.dominio.erros import PermissaoNegada
from assura.identidade.dominio.senha import validar_senha


class RedefinirSenha:
    """Define uma senha provisória; o usuário só consegue trocá-la até escolher a dele.

    Nesta etapa só o administrador do sistema redefine. O administrador da empresa (1.5) poderá
    redefinir apenas a senha de quem tem vínculo ativo só com a empresa dele: senão ele entraria
    nas outras empresas como esse usuário.
    """

    def __init__(
        self,
        usuarios: Usuarios,
        gerador_de_resumo: GeradorDeResumoDeSenha,
        registrar_acao: RegistrarAcao,
    ) -> None:
        self._usuarios = usuarios
        self._gerador_de_resumo = gerador_de_resumo
        self._registrar_acao = registrar_acao

    def executar(
        self, *, solicitante: UsuarioAutenticado, usuario_id: UUID, senha_provisoria: str
    ) -> None:
        if not solicitante.administrador_do_sistema:
            raise PermissaoNegada("só o administrador do sistema redefine senhas")
        usuario = self._usuarios.obter(usuario_id)
        resumo = self._gerador_de_resumo.gerar(validar_senha(senha_provisoria))
        usuario.definir_senha_provisoria(resumo)
        self._usuarios.atualizar(usuario)
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.SENHA_REDEFINIDA,
            usuario_id=usuario.id,
        )
