import pytest

from assura.identidade.dominio.email import TAMANHO_MAXIMO_DE_EMAIL, Email
from assura.identidade.dominio.erros import EmailInvalido


@pytest.mark.parametrize(
    ("texto", "valor"),
    [
        ("maria@empresa.com", "maria@empresa.com"),
        ("  Maria.Souza@Empresa.COM.br ", "maria.souza@empresa.com.br"),
        ("joao+auditoria@sub.empresa.com", "joao+auditoria@sub.empresa.com"),
    ],
)
def test_email_valido_e_guardado_em_minusculas(texto: str, valor: str) -> None:
    assert Email.criar(texto).valor == valor


def test_email_com_maiusculas_diferentes_e_o_mesmo_email() -> None:
    assert Email.criar("Maria@Empresa.com") == Email.criar("maria@empresa.com")


@pytest.mark.parametrize(
    "texto",
    [
        "",
        "maria",
        "maria@",
        "@empresa.com",
        "maria@empresa",
        "maria souza@empresa.com",
        "maria@@empresa.com",
        "maria@empresa.com.",
        "a" * (TAMANHO_MAXIMO_DE_EMAIL - len("@empresa.com") + 1) + "@empresa.com",
    ],
)
def test_email_invalido_e_recusado(texto: str) -> None:
    with pytest.raises(EmailInvalido):
        Email.criar(texto)


def test_email_no_tamanho_maximo_e_aceito() -> None:
    texto = "a" * (TAMANHO_MAXIMO_DE_EMAIL - len("@empresa.com")) + "@empresa.com"

    assert len(Email.criar(texto).valor) == TAMANHO_MAXIMO_DE_EMAIL
