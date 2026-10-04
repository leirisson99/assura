from typing import Any

from fastapi.testclient import TestClient

from tests.apoio import gerar_cnpj_valido

EMAIL_DO_ROOT = "root@assura.local"
SENHA_INICIAL = "senha-provisoria-1"
SENHA_DEFINITIVA = "senha-definitiva-2"


def entrar(cliente: TestClient, email: str, senha: str) -> dict[str, str]:
    resposta = cliente.post("/autenticacao/login", json={"email": email, "senha": senha})
    assert resposta.status_code == 200, resposta.text
    return {"Authorization": f"Bearer {resposta.json()['token']}"}


def responder(
    cliente: TestClient,
    metodo: str,
    rota: str,
    cabecalhos: dict[str, str],
    esperado: int,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    resposta = cliente.request(metodo, rota, headers=cabecalhos, json=json, params=params)
    assert resposta.status_code == esperado, f"{metodo} {rota}: {resposta.text}"
    return resposta.json() if resposta.content else None


def cadastrar_empresa(cliente: TestClient, cabecalhos: dict[str, str], nome: str) -> Any:
    return responder(
        cliente,
        "POST",
        "/empresas",
        cabecalhos,
        201,
        json={"razao_social": nome, "cnpj": gerar_cnpj_valido()},
    )


def incluir_pessoa(
    cliente: TestClient, cabecalhos: dict[str, str], empresa_id: str, email: str
) -> Any:
    return responder(
        cliente,
        "POST",
        f"/empresas/{empresa_id}/usuarios",
        cabecalhos,
        201,
        json={"nome": email.split("@")[0], "email": email},
    )


def dar_acesso(
    cliente: TestClient, cabecalhos_do_root: dict[str, str], usuario_id: str, email: str
) -> dict[str, str]:
    """Define a senha provisória, entra, troca pela definitiva e devolve a sessão pronta."""
    responder(
        cliente,
        "POST",
        f"/usuarios/{usuario_id}/senha",
        cabecalhos_do_root,
        204,
        json={"senha_provisoria": SENHA_INICIAL},
    )
    cabecalhos = entrar(cliente, email, SENHA_INICIAL)
    responder(
        cliente,
        "POST",
        "/autenticacao/eu/senha",
        cabecalhos,
        204,
        json={"senha_atual": SENHA_INICIAL, "nova_senha": SENHA_DEFINITIVA},
    )
    return cabecalhos
