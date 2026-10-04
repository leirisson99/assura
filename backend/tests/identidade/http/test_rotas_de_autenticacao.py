from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from assura.compartilhado.infraestrutura.http import obter_sessao_do_banco
from assura.historico import RegistrarAcao
from assura.identidade import Usuario, Usuarios
from assura.identidade.aplicacao.portas import GeradorDeResumoDeSenha
from assura.identidade.infraestrutura.sessao_jwt import EmissorDeSessaoJwt
from assura.main import app
from tests.identidade.apoio import (
    CHAVE_DE_SESSAO_DE_TESTE,
    EMAIL,
    OUTRA_SENHA,
    OUTRO_EMAIL,
    SENHA,
    criar_usuario_com_senha,
)


@pytest.fixture
def cliente(sessao: Session) -> Iterator[TestClient]:
    def usar_sessao_de_teste() -> Iterator[Session]:
        yield sessao

    app.dependency_overrides[obter_sessao_do_banco] = usar_sessao_de_teste
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def usuario(
    usuarios: Usuarios, registrar_acao: RegistrarAcao, gerador_de_resumo: GeradorDeResumoDeSenha
) -> Usuario:
    return criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)


def entrar(cliente: TestClient, email: str = EMAIL, senha: str = SENHA) -> dict[str, str]:
    resposta = cliente.post("/autenticacao/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['token']}"}


def test_login_devolve_token_e_situacao_da_senha(cliente: TestClient, usuario: Usuario) -> None:
    resposta = cliente.post("/autenticacao/login", json={"email": EMAIL, "senha": SENHA})

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["tipo"] == "bearer"
    assert corpo["token"]
    assert corpo["senha_provisoria"] is False
    assert corpo["expira_em"]


@pytest.mark.parametrize(
    ("email", "senha"), [(EMAIL, "senha-errada-999"), ("ninguem@empresa.com", SENHA)]
)
def test_login_com_falha_responde_401_sempre_igual(
    cliente: TestClient, usuario: Usuario, email: str, senha: str
) -> None:
    resposta = cliente.post("/autenticacao/login", json={"email": email, "senha": senha})

    assert resposta.status_code == 401
    assert resposta.json() == {"detail": "e-mail ou senha incorretos"}


def test_quem_sou_eu_com_sessao_valida(cliente: TestClient, usuario: Usuario) -> None:
    resposta = cliente.get("/autenticacao/eu", headers=entrar(cliente))

    assert resposta.status_code == 200
    assert resposta.json() == {
        "id": str(usuario.id),
        "nome": usuario.nome,
        "email": EMAIL,
        "administrador_do_sistema": False,
        "senha_provisoria": False,
    }


def criar_token(usuario_id: UUID, emitido_em: datetime) -> str:
    emissor = EmissorDeSessaoJwt(
        chave=CHAVE_DE_SESSAO_DE_TESTE, validade=timedelta(hours=8), relogio=lambda: emitido_em
    )
    return emissor.emitir(usuario_id).token


@pytest.mark.parametrize(
    "cabecalhos",
    [
        {},
        {"Authorization": "Bearer invalido"},
        {"Authorization": "Basic dXN1YXJpbzpzZW5oYQ=="},
    ],
)
def test_sessao_ausente_ou_invalida_responde_401(
    cliente: TestClient, cabecalhos: dict[str, str]
) -> None:
    resposta = cliente.get("/autenticacao/eu", headers=cabecalhos)

    assert resposta.status_code == 401
    assert resposta.headers["www-authenticate"] == "Bearer"


def test_sessao_vencida_responde_401(cliente: TestClient, usuario: Usuario) -> None:
    vencido = criar_token(usuario.id, datetime.now(UTC) - timedelta(hours=9))

    resposta = cliente.get("/autenticacao/eu", headers={"Authorization": f"Bearer {vencido}"})

    assert resposta.status_code == 401


def test_sessao_de_usuario_inexistente_responde_401(cliente: TestClient) -> None:
    token = criar_token(uuid4(), datetime.now(UTC))

    resposta = cliente.get("/autenticacao/eu", headers={"Authorization": f"Bearer {token}"})

    assert resposta.status_code == 401


def test_trocar_a_propria_senha(cliente: TestClient, usuario: Usuario) -> None:
    cabecalhos = entrar(cliente)

    resposta = cliente.post(
        "/autenticacao/eu/senha",
        json={"senha_atual": SENHA, "nova_senha": OUTRA_SENHA},
        headers=cabecalhos,
    )

    assert resposta.status_code == 204
    entrar(cliente, senha=OUTRA_SENHA)


@pytest.mark.parametrize(
    ("senha_atual", "nova_senha"), [("senha-errada-999", OUTRA_SENHA), (SENHA, "curta")]
)
def test_troca_de_senha_recusada_responde_422(
    cliente: TestClient, usuario: Usuario, senha_atual: str, nova_senha: str
) -> None:
    resposta = cliente.post(
        "/autenticacao/eu/senha",
        json={"senha_atual": senha_atual, "nova_senha": nova_senha},
        headers=entrar(cliente),
    )

    assert resposta.status_code == 422


@pytest.fixture
def cabecalhos_do_administrador(
    cliente: TestClient,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
) -> dict[str, str]:
    criar_usuario_com_senha(
        usuarios,
        registrar_acao,
        gerador_de_resumo,
        email="admin@assura.local",
        administrador_do_sistema=True,
    )
    return entrar(cliente, email="admin@assura.local")


def test_administrador_redefine_senha_e_usuario_so_pode_troca_la(
    cliente: TestClient, usuario: Usuario, cabecalhos_do_administrador: dict[str, str]
) -> None:
    resposta = cliente.post(
        f"/usuarios/{usuario.id}/senha",
        json={"senha_provisoria": OUTRA_SENHA},
        headers=cabecalhos_do_administrador,
    )
    assert resposta.status_code == 204

    cabecalhos = entrar(cliente, senha=OUTRA_SENHA)
    assert cliente.get("/autenticacao/eu", headers=cabecalhos).json()["senha_provisoria"]
    bloqueada = cliente.post(
        f"/usuarios/{usuario.id}/senha", json={"senha_provisoria": SENHA}, headers=cabecalhos
    )
    assert bloqueada.status_code == 403

    trocada = cliente.post(
        "/autenticacao/eu/senha",
        json={"senha_atual": OUTRA_SENHA, "nova_senha": SENHA},
        headers=cabecalhos,
    )
    assert trocada.status_code == 204
    assert not cliente.get("/autenticacao/eu", headers=cabecalhos).json()["senha_provisoria"]


def test_quem_nao_e_administrador_recebe_403_ao_redefinir(
    cliente: TestClient,
    usuario: Usuario,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
) -> None:
    outro = criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo, email=OUTRO_EMAIL)

    resposta = cliente.post(
        f"/usuarios/{outro.id}/senha",
        json={"senha_provisoria": OUTRA_SENHA},
        headers=entrar(cliente),
    )

    assert resposta.status_code == 403


def test_redefinir_senha_de_usuario_inexistente_responde_404(
    cliente: TestClient, cabecalhos_do_administrador: dict[str, str]
) -> None:
    resposta = cliente.post(
        f"/usuarios/{uuid4()}/senha",
        json={"senha_provisoria": OUTRA_SENHA},
        headers=cabecalhos_do_administrador,
    )

    assert resposta.status_code == 404
