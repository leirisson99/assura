"""CS-003: o fluxo completo da etapa 1, só por HTTP."""

from fastapi.testclient import TestClient

from tests.identidade.http.apoio_http import (
    cadastrar_empresa,
    dar_acesso,
    incluir_pessoa,
    responder,
)


def test_do_cadastro_da_empresa_ao_administrador_incluindo_pessoas(
    cliente: TestClient, cabecalhos_do_root: dict[str, str]
) -> None:
    empresa_a = cadastrar_empresa(cliente, cabecalhos_do_root, "Empresa A")
    empresa_b = cadastrar_empresa(cliente, cabecalhos_do_root, "Empresa B")

    maria = incluir_pessoa(cliente, cabecalhos_do_root, empresa_a["id"], "maria@a.com")
    responder(
        cliente,
        "POST",
        f"/vinculos/{maria['vinculo']['id']}/administrador",
        cabecalhos_do_root,
        200,
    )
    cabecalhos_da_maria = dar_acesso(
        cliente, cabecalhos_do_root, maria["usuario"]["id"], "maria@a.com"
    )

    joao = incluir_pessoa(cliente, cabecalhos_da_maria, empresa_a["id"], "joao@a.com")
    responder(
        cliente,
        "POST",
        f"/usuarios/{joao['usuario']['id']}/senha",
        cabecalhos_da_maria,
        204,
        json={"senha_provisoria": "provisoria-do-joao"},
    )

    usuarios_de_a = responder(
        cliente, "GET", f"/empresas/{empresa_a['id']}/usuarios", cabecalhos_da_maria, 200
    )
    assert [item["usuario"]["email"] for item in usuarios_de_a] == ["joao@a.com", "maria@a.com"]

    historico_de_a = responder(
        cliente, "GET", f"/empresas/{empresa_a['id']}/historico", cabecalhos_da_maria, 200
    )
    tipos = {registro["tipo_de_acao"] for registro in historico_de_a}
    assert {"empresa_cadastrada", "usuario_vinculado", "administrador_definido"} <= tipos
    assert all(registro["empresa_id"] == empresa_a["id"] for registro in historico_de_a)

    responder(cliente, "GET", f"/empresas/{empresa_b['id']}", cabecalhos_da_maria, 403)
    responder(cliente, "GET", f"/empresas/{empresa_b['id']}/historico", cabecalhos_da_maria, 403)

    erro = responder(
        cliente,
        "DELETE",
        f"/vinculos/{maria['vinculo']['id']}/administrador",
        cabecalhos_da_maria,
        409,
    )
    assert "administrador" in erro["detail"]
