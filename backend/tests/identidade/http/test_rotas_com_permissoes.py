from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from tests.identidade.http.apoio_http import (
    cadastrar_empresa,
    dar_acesso,
    incluir_pessoa,
    responder,
)


@pytest.fixture
def cenario(cliente: TestClient, cabecalhos_do_root: dict[str, str]) -> dict[str, Any]:
    """Empresas A e B; Ana administra A; Beto é membro comum de A; Caio é membro de B."""
    empresa_a = cadastrar_empresa(cliente, cabecalhos_do_root, "Empresa A")
    empresa_b = cadastrar_empresa(cliente, cabecalhos_do_root, "Empresa B")
    ana = incluir_pessoa(cliente, cabecalhos_do_root, empresa_a["id"], "ana@a.com")
    beto = incluir_pessoa(cliente, cabecalhos_do_root, empresa_a["id"], "beto@a.com")
    caio = incluir_pessoa(cliente, cabecalhos_do_root, empresa_b["id"], "caio@b.com")
    responder(
        cliente, "POST", f"/vinculos/{ana['vinculo']['id']}/administrador", cabecalhos_do_root, 200
    )
    return {
        "root": cabecalhos_do_root,
        "empresa_a": empresa_a,
        "empresa_b": empresa_b,
        "ana": ana,
        "beto": beto,
        "caio": caio,
        "sessao_da_ana": dar_acesso(cliente, cabecalhos_do_root, ana["usuario"]["id"], "ana@a.com"),
        "sessao_do_beto": dar_acesso(
            cliente, cabecalhos_do_root, beto["usuario"]["id"], "beto@a.com"
        ),
    }


def test_rotas_de_empresas_exclusivas_do_administrador_do_sistema(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    empresa_a = cenario["empresa_a"]["id"]
    dados = {"razao_social": "Nova", "cnpj": cenario["empresa_a"]["cnpj"]}
    for cabecalhos in (cenario["sessao_da_ana"], cenario["sessao_do_beto"]):
        responder(cliente, "GET", "/empresas", cabecalhos, 403)
        responder(cliente, "POST", "/empresas", cabecalhos, 403, json=dados)
        responder(cliente, "PUT", f"/empresas/{empresa_a}", cabecalhos, 403, json=dados)
        responder(cliente, "POST", f"/empresas/{empresa_a}/desativacao", cabecalhos, 403)

    listadas = responder(cliente, "GET", "/empresas", cenario["root"], 200)
    assert {empresa["razao_social"] for empresa in listadas} == {"Empresa A", "Empresa B"}


def test_administradora_ve_a_propria_empresa_e_membro_comum_nao(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    empresa_a = cenario["empresa_a"]["id"]

    empresa = responder(cliente, "GET", f"/empresas/{empresa_a}", cenario["sessao_da_ana"], 200)
    assert empresa["cnpj_formatado"].count(".") == 2

    responder(cliente, "GET", f"/empresas/{empresa_a}", cenario["sessao_do_beto"], 403)
    responder(cliente, "GET", f"/empresas/{empresa_a}/usuarios", cenario["sessao_do_beto"], 403)


def test_administradora_nao_age_em_outra_empresa(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    empresa_b = cenario["empresa_b"]["id"]
    vinculo_do_caio = cenario["caio"]["vinculo"]["id"]
    sessao_da_ana = cenario["sessao_da_ana"]

    responder(cliente, "GET", f"/empresas/{empresa_b}/usuarios", sessao_da_ana, 403)
    responder(
        cliente,
        "POST",
        f"/empresas/{empresa_b}/usuarios",
        sessao_da_ana,
        403,
        json={"nome": "X", "email": "x@b.com"},
    )
    responder(cliente, "POST", f"/vinculos/{vinculo_do_caio}/desativacao", sessao_da_ana, 403)
    responder(cliente, "POST", f"/vinculos/{vinculo_do_caio}/administrador", sessao_da_ana, 403)
    responder(cliente, "GET", f"/usuarios/{cenario['caio']['usuario']['id']}", sessao_da_ana, 403)
    responder(
        cliente,
        "POST",
        f"/usuarios/{cenario['caio']['usuario']['id']}/senha",
        sessao_da_ana,
        403,
        json={"senha_provisoria": "qualquer-senha"},
    )


def test_quem_ve_um_usuario(cliente: TestClient, cenario: dict[str, Any]) -> None:
    beto = cenario["beto"]["usuario"]["id"]

    for cabecalhos in (cenario["root"], cenario["sessao_da_ana"], cenario["sessao_do_beto"]):
        usuario = responder(cliente, "GET", f"/usuarios/{beto}", cabecalhos, 200)
        assert usuario["email"] == "beto@a.com"
        assert "resumo_da_senha" not in usuario

    ana = cenario["ana"]["usuario"]["id"]
    responder(cliente, "GET", f"/usuarios/{ana}", cenario["sessao_do_beto"], 403)


def test_alterar_usuario_so_pelo_administrador_do_sistema(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    beto = cenario["beto"]["usuario"]["id"]
    dados = {"nome": "Beto Silva", "email": "beto@a.com"}

    responder(cliente, "PUT", f"/usuarios/{beto}", cenario["sessao_da_ana"], 403, json=dados)
    alterado = responder(cliente, "PUT", f"/usuarios/{beto}", cenario["root"], 200, json=dados)
    assert alterado["nome"] == "Beto Silva"


def test_historico_geral_so_para_o_administrador_do_sistema(
    cliente: TestClient, cenario: dict[str, Any]
) -> None:
    responder(cliente, "GET", "/historico", cenario["sessao_da_ana"], 403)

    registros = responder(
        cliente,
        "GET",
        "/historico",
        cenario["root"],
        200,
        params={"tipo_de_acao": "empresa_cadastrada"},
    )
    assert len(registros) == 2


@pytest.mark.parametrize(
    ("metodo", "rota", "corpo", "esperado"),
    [
        ("GET", "/empresas/{nada}", None, 404),
        ("GET", "/usuarios/{nada}", None, 404),
        ("POST", "/vinculos/{nada}/desativacao", None, 404),
        ("POST", "/empresas", {"razao_social": "X", "cnpj": "12.345.678/0001-96"}, 422),
        ("GET", "/empresas?tamanho=500", None, 422),
        ("GET", "/historico?tipo_de_acao=inventada", None, 422),
        ("POST", "/empresas/{empresa_a}/reativacao", None, 409),
        ("POST", "/empresas", {"razao_social": "X", "cnpj": "{cnpj_de_a}"}, 409),
    ],
)
def test_erros_tem_codigos_distintos(
    cliente: TestClient,
    cenario: dict[str, Any],
    metodo: str,
    rota: str,
    corpo: dict[str, str] | None,
    esperado: int,
) -> None:
    valores = {
        "nada": uuid4(),
        "empresa_a": cenario["empresa_a"]["id"],
        "cnpj_de_a": cenario["empresa_a"]["cnpj"],
    }
    corpo_preenchido = (
        {chave: valor.format(**valores) for chave, valor in corpo.items()} if corpo else None
    )

    responder(
        cliente, metodo, rota.format(**valores), cenario["root"], esperado, json=corpo_preenchido
    )
