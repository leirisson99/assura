from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_do_usuario import registrar_acao_sobre_usuario
from assura.identidade.aplicacao.portas import GeradorDeResumoDeSenha, Usuarios
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.erros import AdministradorDoSistemaJaExiste
from assura.identidade.dominio.senha import validar_senha
from assura.identidade.dominio.usuario import Usuario


class CriarRoot:
    """Cria o primeiro administrador do sistema; só funciona enquanto não existe nenhum."""

    def __init__(
        self,
        usuarios: Usuarios,
        gerador_de_resumo: GeradorDeResumoDeSenha,
        registrar_acao: RegistrarAcao,
    ) -> None:
        self._usuarios = usuarios
        self._gerador_de_resumo = gerador_de_resumo
        self._registrar_acao = registrar_acao

    def executar(self, *, nome: str, email: str, senha: str) -> Usuario:
        if self._usuarios.existe_administrador_do_sistema():
            raise AdministradorDoSistemaJaExiste("já existe administrador do sistema")
        root = Usuario.cadastrar(nome=nome, email=Email.criar(email), administrador_do_sistema=True)
        # Quem cria o root digita a própria senha: ela já nasce definitiva.
        root.definir_senha_definitiva(self._gerador_de_resumo.gerar(validar_senha(senha)))
        self._usuarios.adicionar(root)
        registrar_acao_sobre_usuario(
            self._registrar_acao,
            autor=Autor.sistema(),
            tipo_de_acao=TipoDeAcao.USUARIO_CADASTRADO,
            usuario_id=root.id,
            detalhes={"administrador_do_sistema": True},
        )
        return root
