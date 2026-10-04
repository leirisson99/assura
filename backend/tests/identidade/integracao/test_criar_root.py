import pytest
from sqlalchemy.orm import Session

from assura.historico import Autor, RegistrarAcao
from assura.identidade import (
    AdministradorDoSistemaJaExiste,
    CriarRoot,
    SenhaInvalida,
    Usuarios,
)
from assura.identidade.aplicacao.portas import GeradorDeResumoDeSenha
from assura.identidade.dominio.email import Email
from tests.identidade.apoio import SENHA, ler_historico_do_objeto


def criar_root(
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    registrar_acao: RegistrarAcao,
    senha: str = SENHA,
) -> None:
    CriarRoot(usuarios, gerador_de_resumo, registrar_acao).executar(
        nome="Administrador", email="Admin@Assura.local", senha=senha
    )


def test_root_e_criado_administrador_do_sistema_com_senha_definitiva(
    sessao: Session,
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    registrar_acao: RegistrarAcao,
) -> None:
    criar_root(usuarios, gerador_de_resumo, registrar_acao)

    root = usuarios.obter_por_email(Email.criar("admin@assura.local"))
    assert root is not None
    assert root.administrador_do_sistema
    assert not root.senha_provisoria
    assert root.resumo_da_senha is not None
    assert gerador_de_resumo.conferir(root.resumo_da_senha, SENHA)
    [registro] = ler_historico_do_objeto(sessao, "usuario", root.id)
    assert registro.tipo_de_acao == "usuario_cadastrado"
    assert registro.autor == Autor.sistema()
    assert registro.detalhes == {"administrador_do_sistema": True}


def test_segundo_root_e_recusado(
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    registrar_acao: RegistrarAcao,
) -> None:
    criar_root(usuarios, gerador_de_resumo, registrar_acao)

    with pytest.raises(AdministradorDoSistemaJaExiste):
        CriarRoot(usuarios, gerador_de_resumo, registrar_acao).executar(
            nome="Outro", email="outro@assura.local", senha=SENHA
        )

    assert usuarios.obter_por_email(Email.criar("outro@assura.local")) is None


def test_root_com_senha_invalida_e_recusado(
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    registrar_acao: RegistrarAcao,
) -> None:
    with pytest.raises(SenhaInvalida):
        criar_root(usuarios, gerador_de_resumo, registrar_acao, senha="curta")

    assert not usuarios.existe_administrador_do_sistema()
