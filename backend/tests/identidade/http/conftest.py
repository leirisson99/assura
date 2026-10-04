from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from assura.compartilhado.infraestrutura.http import obter_sessao_do_banco
from assura.historico import RegistrarAcao
from assura.identidade import Usuarios
from assura.identidade.aplicacao.portas import GeradorDeResumoDeSenha
from assura.identidade.infraestrutura.dependencias_http import obter_gerador_de_resumo
from assura.identidade.infraestrutura.resumo_de_senha_argon2 import GeradorDeResumoArgon2
from assura.main import app
from tests.apoio import GERADOR_DE_RESUMO_RAPIDO
from tests.identidade.apoio import SENHA, criar_usuario_com_senha
from tests.identidade.http.apoio_http import EMAIL_DO_ROOT, entrar


@pytest.fixture
def cliente(sessao: Session) -> Iterator[TestClient]:
    """Cliente HTTP que usa a sessão do teste: nada fica gravado depois do teste."""

    def usar_sessao_de_teste() -> Iterator[Session]:
        yield sessao

    app.dependency_overrides[obter_sessao_do_banco] = usar_sessao_de_teste
    app.dependency_overrides[obter_gerador_de_resumo] = lambda: GeradorDeResumoArgon2(
        GERADOR_DE_RESUMO_RAPIDO
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def cabecalhos_do_root(
    cliente: TestClient,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
) -> dict[str, str]:
    criar_usuario_com_senha(
        usuarios,
        registrar_acao,
        gerador_de_resumo,
        email=EMAIL_DO_ROOT,
        senha=SENHA,
        administrador_do_sistema=True,
    )
    return entrar(cliente, EMAIL_DO_ROOT, SENHA)
