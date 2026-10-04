import pytest

from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.erros import CnpjInvalido


@pytest.mark.parametrize(
    ("texto", "valor"),
    [
        ("12345678000195", "12345678000195"),
        ("12.345.678/0001-95", "12345678000195"),
        ("  11.222.333/0001-81 ", "11222333000181"),
        ("12.ABC.345/01DE-35", "12ABC34501DE35"),
        ("12ABC34501DE35", "12ABC34501DE35"),
        ("12.abc.345/01de-35", "12ABC34501DE35"),
    ],
)
def test_cnpj_valido_e_guardado_sem_mascara_e_em_maiusculas(texto: str, valor: str) -> None:
    assert Cnpj.criar(texto).valor == valor


def test_cnpj_com_e_sem_mascara_sao_o_mesmo_cnpj() -> None:
    assert Cnpj.criar("12.345.678/0001-95") == Cnpj.criar("12345678000195")


@pytest.mark.parametrize(
    "texto",
    [
        "12345678000196",  # segundo dígito verificador errado
        "12345678000185",  # primeiro dígito verificador errado
        "12.ABC.345/01DE-34",  # alfanumérico com dígito errado
        "1234567800019",  # 13 caracteres
        "123456780001955",  # 15 caracteres
        "12ABC34501DE3A",  # letra no dígito verificador
        "12ABC345#1DE35",  # caractere fora de [0-9A-Z]
        "",
    ],
)
def test_cnpj_invalido_e_recusado(texto: str) -> None:
    with pytest.raises(CnpjInvalido):
        Cnpj.criar(texto)


@pytest.mark.parametrize("texto", ["00000000000000", "11111111111111", "99.999.999/9999-99"])
def test_cnpj_com_um_so_caractere_repetido_e_recusado(texto: str) -> None:
    with pytest.raises(CnpjInvalido):
        Cnpj.criar(texto)


@pytest.mark.parametrize(
    ("texto", "formatado"),
    [
        ("12345678000195", "12.345.678/0001-95"),
        ("12ABC34501DE35", "12.ABC.345/01DE-35"),
    ],
)
def test_cnpj_formatado_usa_a_mascara_oficial(texto: str, formatado: str) -> None:
    assert Cnpj.criar(texto).formatado == formatado


def test_cnpj_construido_direto_tambem_e_validado() -> None:
    with pytest.raises(CnpjInvalido):
        Cnpj("12345678000196")
