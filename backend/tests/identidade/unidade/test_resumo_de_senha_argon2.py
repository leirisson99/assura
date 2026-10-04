from assura.identidade.infraestrutura.resumo_de_senha_argon2 import GeradorDeResumoArgon2

gerador = GeradorDeResumoArgon2()


def test_resumo_nao_contem_a_senha_e_usa_argon2id() -> None:
    resumo = gerador.gerar("senha-secreta")

    assert "senha-secreta" not in resumo
    assert resumo.startswith("$argon2id$")


def test_mesma_senha_gera_resumos_diferentes() -> None:
    assert gerador.gerar("senha-secreta") != gerador.gerar("senha-secreta")


def test_senha_correta_confere_com_o_resumo() -> None:
    assert gerador.conferir(gerador.gerar("senha-secreta"), "senha-secreta")


def test_senha_errada_nao_confere() -> None:
    assert not gerador.conferir(gerador.gerar("senha-secreta"), "senha-errada")


def test_resumo_invalido_nao_confere() -> None:
    assert not gerador.conferir("nao-e-um-resumo", "senha-secreta")
