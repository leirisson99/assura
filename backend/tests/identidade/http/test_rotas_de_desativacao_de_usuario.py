from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.identidade.http.apoio_http import (
    SENHA_DEFINITIVA,
    cadastrar_empresa,
    dar_acesso,
    entrar,
    incluir_pessoa,
    responder,
)


@pytest.fixture
def cenario(cliente: TestClient, cabecalhos_do_root: dict[str, str]) -> dict[str, Any]:
    """Empresa A; Ana a administra; Beto é membro comum de A, com sessão aberta."""
    empresa_a = cadastrar_empresa(cliente, cabecalhos_do_root, "Empresa A")
    ana = incluir_pessoa(cliente, cabecalhos_do_root, empresa_a["id"], "ana@a.com")
    beto = incluir_pessoa(cliente, cabecalhos_do_root, empresa_a["id"], "beto@a.com")
    responder(
        cliente, "POST", f"/vinculos/{ana['vinculo']['id']}/administrador", cabecalhos_do_root, 200
    )
    return {
        "root": cabecalhos_do_root,
        "empresa_a": empresa_a,
        "ana": ana["usuario"],
        "beto": beto["usuario"],
        "sessao_da_ana": dar_acesso(cliente, cabecalhos_do_root, ana["usuario"]["id"], "ana@a.com"),
        "sessao_do_beto": dar_acesso(
            cliente, cabecalhos_do_root, beto["usuario"]["id"], "beto@a.com"
        ),
    }


def test_root_desativa_e_reativa_usuario_e_o_acesso_acompanha(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    root, beto = cenario["root"], cenario["beto"]

    desativado = responder(cliente, "POST", f"/usuarios/{beto['id']}/desativacao", root, 200)

    assert desativado["situacao"] == "desativado"
    responder(cliente, "GET", "/autenticacao/eu", cenario["sessao_do_beto"], 401)
    login = cliente.post(
        "/autenticacao/login", json={"email": "beto@a.com", "senha": SENHA_DEFINITIVA}
    )
    assert login.status_code == 401
    assert login.json()["detail"] == "e-mail ou senha incorretos"

    reativado = responder(cliente, "POST", f"/usuarios/{beto['id']}/reativacao", root, 200)

    assert reativado["situacao"] == "ativo"
    entrar(cliente, "beto@a.com", SENHA_DEFINITIVA)


def test_so_o_administrador_do_sistema_desativa_e_reativa(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    beto = cenario["beto"]

    for sessao in (cenario["sessao_da_ana"], cenario["sessao_do_beto"]):
        responder(cliente, "POST", f"/usuarios/{beto['id']}/desativacao", sessao, 403)
        responder(cliente, "POST", f"/usuarios/{beto['id']}/reativacao", sessao, 403)


def test_usuario_inexistente_responde_nao_encontrado(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    responder(cliente, "POST", f"/usuarios/{uuid4()}/desativacao", cenario["root"], 404)
    responder(cliente, "POST", f"/usuarios/{uuid4()}/reativacao", cenario["root"], 404)


def test_conflitos_com_o_estado_respondem_409(cliente: TestClient, cenario: dict[str, Any]) -> None:
    root, ana, beto = cenario["root"], cenario["ana"], cenario["beto"]
    root_id = responder(cliente, "GET", "/autenticacao/eu", root, 200)["id"]

    responder(cliente, "POST", f"/usuarios/{beto['id']}/reativacao", root, 409)
    responder(cliente, "POST", f"/usuarios/{beto['id']}/desativacao", root, 200)
    responder(cliente, "POST", f"/usuarios/{beto['id']}/desativacao", root, 409)
    ultima_administradora = responder(
        cliente, "POST", f"/usuarios/{ana['id']}/desativacao", root, 409
    )
    assert "Empresa A" in ultima_administradora["detail"]
    responder(cliente, "POST", f"/usuarios/{root_id}/desativacao", root, 409)


def test_lista_da_empresa_mostra_o_usuario_desativado(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    root, beto = cenario["root"], cenario["beto"]
    responder(cliente, "POST", f"/usuarios/{beto['id']}/desativacao", root, 200)

    lista = responder(
        cliente,
        "GET",
        f"/empresas/{cenario['empresa_a']['id']}/usuarios",
        cenario["sessao_da_ana"],
        200,
    )

    situacoes = {item["usuario"]["email"]: item["usuario"]["situacao"] for item in lista}
    assert situacoes["beto@a.com"] == "desativado"
    assert situacoes["ana@a.com"] == "ativo"
