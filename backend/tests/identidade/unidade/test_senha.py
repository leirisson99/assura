import pytest

from assura.identidade.dominio.erros import SenhaInvalida
from assura.identidade.dominio.senha import (
    TAMANHO_MAXIMO_DE_SENHA,
    TAMANHO_MINIMO_DE_SENHA,
    validar_senha,
)


@pytest.mark.parametrize(
    "senha",
    [
        "a" * TAMANHO_MINIMO_DE_SENHA,
        "a" * TAMANHO_MAXIMO_DE_SENHA,
        "frase longa sem numero",
        "  com espacos  ",
        "çãõ€漢字🔒senha",
    ],
)
def test_senha_dentro_dos_limites_e_aceita_como_digitada(senha: str) -> None:
    assert validar_senha(senha) == senha


@pytest.mark.parametrize(
    "senha", ["", "a" * (TAMANHO_MINIMO_DE_SENHA - 1), "a" * (TAMANHO_MAXIMO_DE_SENHA + 1)]
)
def test_senha_fora_dos_limites_e_recusada(senha: str) -> None:
    with pytest.raises(SenhaInvalida):
        validar_senha(senha)
