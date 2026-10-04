from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_usuario
from assura.identidade.aplicacao.permissoes import exigir_administrador_do_sistema
from assura.identidade.aplicacao.portas import UsuarioAutenticado, Usuarios
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.erros import EmailJaCadastrado
from assura.identidade.dominio.usuario import Usuario


class CadastrarUsuario:
    def __init__(self, usuarios: Usuarios, registrar_acao: RegistrarAcao) -> None:
        self._usuarios = usuarios
        self._registrar_acao = registrar_acao

    def executar(self, *, solicitante: UsuarioAutenticado, nome: str, email: str) -> Usuario:
        exigir_administrador_do_sistema(solicitante)
        usuario = Usuario.cadastrar(nome=nome, email=Email.criar(email))
        if self._usuarios.existe_email(usuario.email):
            raise EmailJaCadastrado(f"já existe usuário com o e-mail {usuario.email.valor}")
        self._usuarios.adicionar(usuario)
        # Sem detalhes: nome e e-mail são dados pessoais e já estão no próprio usuário.
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.USUARIO_CADASTRADO,
            usuario_id=usuario.id,
        )
        return usuario
