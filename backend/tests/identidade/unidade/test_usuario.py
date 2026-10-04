import pytest

from assura.identidade.dominio.email import Email
from assura.identidade.dominio.erros import (
    NomeDeUsuarioInvalido,
    UsuarioJaAtivo,
    UsuarioJaDesativado,
)
from assura.identidade.dominio.usuario import (
    TAMANHO_MAXIMO_DE_NOME_DE_USUARIO,
    SituacaoDoUsuario,
    Usuario,
)

EMAIL = Email.criar("maria@empresa.com")


def cadastrar(nome: str = "Maria Souza") -> Usuario:
    return Usuario.cadastrar(nome=nome, email=EMAIL)


def test_usuario_nasce_ativo_com_os_dados_informados() -> None:
    usuario = cadastrar(" Maria Souza ")

    assert usuario.nome == "Maria Souza"
    assert usuario.email == EMAIL
    assert usuario.situacao is SituacaoDoUsuario.ATIVO


@pytest.mark.parametrize("nome", ["", "   ", "M" * (TAMANHO_MAXIMO_DE_NOME_DE_USUARIO + 1)])
def test_nome_vazio_ou_longo_demais_e_recusado(nome: str) -> None:
    with pytest.raises(NomeDeUsuarioInvalido):
        cadastrar(nome)


def test_alterar_dados_devolve_apenas_os_campos_alterados() -> None:
    usuario = cadastrar()

    alteracoes = usuario.alterar_dados(nome="Maria S. Souza", email=EMAIL)

    assert alteracoes == {"nome": {"anterior": "Maria Souza", "novo": "Maria S. Souza"}}
    assert usuario.nome == "Maria S. Souza"


def test_alterar_dados_sem_mudanca_devolve_nada_alterado() -> None:
    usuario = cadastrar()

    assert usuario.alterar_dados(nome="Maria Souza", email=Email.criar("MARIA@empresa.com")) == {}


def test_alterar_dados_invalidos_nao_muda_o_usuario() -> None:
    usuario = cadastrar()

    with pytest.raises(NomeDeUsuarioInvalido):
        usuario.alterar_dados(nome="", email=Email.criar("outro@empresa.com"))

    assert usuario.nome == "Maria Souza"
    assert usuario.email == EMAIL


def test_usuario_cadastrado_nao_tem_senha_nem_e_administrador_do_sistema() -> None:
    usuario = cadastrar()

    assert not usuario.tem_senha
    assert not usuario.senha_provisoria
    assert not usuario.administrador_do_sistema


def test_senha_provisoria_fica_marcada_como_provisoria() -> None:
    usuario = cadastrar()

    usuario.definir_senha_provisoria("resumo-provisorio")

    assert usuario.tem_senha
    assert usuario.resumo_da_senha == "resumo-provisorio"
    assert usuario.senha_provisoria


def test_senha_definitiva_substitui_a_provisoria() -> None:
    usuario = cadastrar()
    usuario.definir_senha_provisoria("resumo-provisorio")

    usuario.definir_senha_definitiva("resumo-definitivo")

    assert usuario.resumo_da_senha == "resumo-definitivo"
    assert not usuario.senha_provisoria


def test_desativar_usuario_ativo_o_deixa_desativado() -> None:
    usuario = cadastrar()

    usuario.desativar()

    assert usuario.situacao is SituacaoDoUsuario.DESATIVADO
    assert not usuario.esta_ativo


def test_desativar_usuario_ja_desativado_e_recusado() -> None:
    usuario = cadastrar()
    usuario.desativar()

    with pytest.raises(UsuarioJaDesativado):
        usuario.desativar()


def test_reativar_usuario_desativado_o_deixa_ativo() -> None:
    usuario = cadastrar()
    usuario.desativar()

    usuario.reativar()

    assert usuario.situacao is SituacaoDoUsuario.ATIVO
    assert usuario.esta_ativo


def test_reativar_usuario_ja_ativo_e_recusado() -> None:
    usuario = cadastrar()

    with pytest.raises(UsuarioJaAtivo):
        usuario.reativar()


def test_desativar_nao_muda_dados_senha_nem_administrador_do_sistema() -> None:
    usuario = Usuario.cadastrar(nome="Root", email=EMAIL, administrador_do_sistema=True)
    usuario.definir_senha_definitiva("resumo-definitivo")

    usuario.desativar()

    assert usuario.nome == "Root"
    assert usuario.email == EMAIL
    assert usuario.resumo_da_senha == "resumo-definitivo"
    assert not usuario.senha_provisoria
    assert usuario.administrador_do_sistema
