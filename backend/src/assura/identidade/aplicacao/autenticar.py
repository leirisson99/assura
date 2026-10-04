from dataclasses import dataclass

from assura.identidade.aplicacao.portas import (
    EmissorDeSessao,
    GeradorDeResumoDeSenha,
    SessaoEmitida,
    Usuarios,
)
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.erros import CredenciaisInvalidas, EmailInvalido
from assura.identidade.dominio.usuario import SituacaoDoUsuario, Usuario

MENSAGEM_DE_CREDENCIAIS_INVALIDAS = "e-mail ou senha incorretos"


# Resumo argon2id de uma senha aleatória descartada, com os parâmetros padrão: conferir contra ele
# leva o mesmo tempo que conferir contra o resumo de um usuário real.
RESUMO_DESCARTAVEL = (
    "$argon2id$v=19$m=65536,t=3,p=4$"
    "1eC91Yi/mldVvdZLCD8wnA$e1xk8H9qwJkrAC4X9UsPKUHB98BS5ujuiNJpqUUdAkk"
)


class Autenticar:
    @dataclass(frozen=True)
    class Resultado:
        sessao: SessaoEmitida
        senha_provisoria: bool

    def __init__(
        self,
        usuarios: Usuarios,
        gerador_de_resumo: GeradorDeResumoDeSenha,
        emissor_de_sessao: EmissorDeSessao,
    ) -> None:
        self._usuarios = usuarios
        self._gerador_de_resumo = gerador_de_resumo
        self._emissor_de_sessao = emissor_de_sessao

    def executar(self, *, email: str, senha: str) -> Resultado:
        usuario = self._buscar_usuario_que_pode_entrar(email)
        # Sem usuário, a senha é conferida contra um resumo descartável: o tempo de resposta
        # não pode revelar se o e-mail está cadastrado.
        resumo = (
            usuario.resumo_da_senha
            if usuario is not None and usuario.resumo_da_senha is not None
            else RESUMO_DESCARTAVEL
        )
        senha_confere = self._gerador_de_resumo.conferir(resumo, senha)
        if usuario is None or not senha_confere:
            raise CredenciaisInvalidas(MENSAGEM_DE_CREDENCIAIS_INVALIDAS)
        return self.Resultado(
            sessao=self._emissor_de_sessao.emitir(usuario.id),
            senha_provisoria=usuario.senha_provisoria,
        )

    def _buscar_usuario_que_pode_entrar(self, email: str) -> Usuario | None:
        try:
            usuario = self._usuarios.obter_por_email(Email.criar(email))
        except EmailInvalido:
            return None
        if usuario is None or not usuario.tem_senha:
            return None
        if usuario.situacao is not SituacaoDoUsuario.ATIVO:
            return None
        return usuario
