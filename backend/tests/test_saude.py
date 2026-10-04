from fastapi.testclient import TestClient

from assura.main import app


def test_endpoint_de_saude_responde_ok() -> None:
    cliente = TestClient(app)

    resposta = cliente.get("/saude")

    assert resposta.status_code == 200
    assert resposta.json() == {"situacao": "ok"}
