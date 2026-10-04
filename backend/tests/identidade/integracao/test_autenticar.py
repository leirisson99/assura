import pytest

from assura.historico import RegistrarAcao
from assura.identidade import Autenticar, CredenciaisInvalidas, Usuarios
from assura.identidade.aplicacao.portas import EmissorDeSessao, GeradorDeResumoDeSenha
from tests.identidade.apoio import (
    EMAIL,
    OUTRO_EMAIL,
    SENHA,
    cadastrar_usuario,
    criar_usuario_com_senha,
)


def autenticar(
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    emissor_de_sessao: EmissorDeSessao,
    email: str,
    senha: str,
) -> Autenticar.Resultado:
    return Autenticar(usuarios, gerador_de_resumo, emissor_de_sessao).executar(
        email=email, senha=senha
    )


@pytest.mark.parametrize("senha_provisoria", [False, True])
def test_credenciais_corretas_emitem_sessao_do_usuario(
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    emissor_de_sessao: EmissorDeSessao,
    senha_provisoria: bool,
) -> None:
    usuario = criar_usuario_com_senha(
        usuarios, registrar_acao, gerador_de_resumo, senha_provisoria=senha_provisoria
    )

    resultado = autenticar(usuarios, gerador_de_resumo, emissor_de_sessao, EMAIL, SENHA)

    assert emissor_de_sessao.ler(resultado.sessao.token) == usuario.id
    assert resultado.senha_provisoria is senha_provisoria


def test_email_com_outras_maiusculas_e_aceito(
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    emissor_de_sessao: EmissorDeSessao,
) -> None:
    criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)

    autenticar(usuarios, gerador_de_resumo, emissor_de_sessao, f"  {EMAIL.upper()} ", SENHA)


@pytest.mark.parametrize(
    ("email", "senha"),
    [
        (EMAIL, "senha-errada-999"),
        ("ninguem@empresa.com", SENHA),
        ("nao-e-email", SENHA),
        (OUTRO_EMAIL, SENHA),  # usuário cadastrado que ainda não recebeu senha
    ],
)
def test_falhas_de_login_dao_sempre_o_mesmo_erro(
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    emissor_de_sessao: EmissorDeSessao,
    email: str,
    senha: str,
) -> None:
    criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)
    cadastrar_usuario(usuarios, registrar_acao, nome="Sem Senha", email=OUTRO_EMAIL)

    with pytest.raises(CredenciaisInvalidas, match="e-mail ou senha incorretos"):
        autenticar(usuarios, gerador_de_resumo, emissor_de_sessao, email, senha)
