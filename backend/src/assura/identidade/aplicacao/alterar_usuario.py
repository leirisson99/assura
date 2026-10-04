from uuid import UUID

from assura.historico import Autor, Detalhes, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_usuario
from assura.identidade.aplicacao.permissoes import exigir_administrador_do_sistema
from assura.identidade.aplicacao.portas import UsuarioAutenticado, Usuarios
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.erros import EmailJaCadastrado
from assura.identidade.dominio.usuario import Usuario


class AlterarUsuario:
    """Substitui nome e e-mail; sem mudança efetiva, nada é gravado nem registrado."""

    def __init__(self, usuarios: Usuarios, registrar_acao: RegistrarAcao) -> None:
        self._usuarios = usuarios
        self._registrar_acao = registrar_acao

    def executar(
        self, *, solicitante: UsuarioAutenticado, usuario_id: UUID, nome: str, email: str
    ) -> Usuario:
        exigir_administrador_do_sistema(solicitante)
        usuario = self._usuarios.obter(usuario_id)
        novo_email = Email.criar(email)
        if self._usuarios.existe_email(novo_email, exceto_usuario_id=usuario.id):
            raise EmailJaCadastrado(f"já existe outro usuário com o e-mail {novo_email.valor}")
        alteracoes = usuario.alterar_dados(nome=nome, email=novo_email)
        if not alteracoes:
            return usuario
        self._usuarios.atualizar(usuario)
        detalhes: Detalhes = {
            campo: {"anterior": alteracao["anterior"], "novo": alteracao["novo"]}
            for campo, alteracao in alteracoes.items()
        }
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.USUARIO_ALTERADO,
            usuario_id=usuario.id,
            detalhes=detalhes,
        )
        return usuario
