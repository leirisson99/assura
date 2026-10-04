import pytest

from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.empresa import (
    TAMANHO_MAXIMO_DE_NOME,
    Empresa,
    SituacaoDaEmpresa,
)
from assura.identidade.dominio.erros import (
    EmpresaJaAtiva,
    EmpresaJaDesativada,
    NomeFantasiaInvalido,
    RazaoSocialInvalida,
)

CNPJ = Cnpj.criar("12.345.678/0001-95")
OUTRO_CNPJ = Cnpj.criar("11.222.333/0001-81")


def cadastrar(
    razao_social: str = "Empresa X Ltda", nome_fantasia: str | None = "Empresa X"
) -> Empresa:
    return Empresa.cadastrar(razao_social=razao_social, nome_fantasia=nome_fantasia, cnpj=CNPJ)


def test_empresa_nasce_ativa_com_os_dados_informados() -> None:
    empresa = cadastrar()

    assert empresa.situacao is SituacaoDaEmpresa.ATIVA
    assert empresa.razao_social == "Empresa X Ltda"
    assert empresa.nome_fantasia == "Empresa X"
    assert empresa.cnpj == CNPJ


def test_espacos_nas_pontas_sao_descartados() -> None:
    empresa = cadastrar(razao_social="  Empresa X Ltda ", nome_fantasia=" Empresa X  ")

    assert empresa.razao_social == "Empresa X Ltda"
    assert empresa.nome_fantasia == "Empresa X"


@pytest.mark.parametrize("nome_fantasia", [None, "", "   "])
def test_nome_fantasia_vazio_vira_nao_informado(nome_fantasia: str | None) -> None:
    assert cadastrar(nome_fantasia=nome_fantasia).nome_fantasia is None


@pytest.mark.parametrize("razao_social", ["", "   ", "X" * (TAMANHO_MAXIMO_DE_NOME + 1)])
def test_razao_social_vazia_ou_longa_demais_e_recusada(razao_social: str) -> None:
    with pytest.raises(RazaoSocialInvalida):
        cadastrar(razao_social=razao_social)


def test_razao_social_no_tamanho_maximo_e_aceita() -> None:
    razao_social = "X" * TAMANHO_MAXIMO_DE_NOME

    assert cadastrar(razao_social=razao_social).razao_social == razao_social


def test_nome_fantasia_longo_demais_e_recusado() -> None:
    with pytest.raises(NomeFantasiaInvalido):
        cadastrar(nome_fantasia="X" * (TAMANHO_MAXIMO_DE_NOME + 1))


def test_empresa_ativa_pode_ser_desativada() -> None:
    empresa = cadastrar()

    empresa.desativar()

    assert empresa.situacao is SituacaoDaEmpresa.DESATIVADA


def test_empresa_desativada_nao_pode_ser_desativada_de_novo() -> None:
    empresa = cadastrar()
    empresa.desativar()

    with pytest.raises(EmpresaJaDesativada):
        empresa.desativar()


def test_empresa_desativada_pode_ser_reativada() -> None:
    empresa = cadastrar()
    empresa.desativar()

    empresa.reativar()

    assert empresa.situacao is SituacaoDaEmpresa.ATIVA


def test_empresa_ativa_nao_pode_ser_reativada() -> None:
    with pytest.raises(EmpresaJaAtiva):
        cadastrar().reativar()


def test_alterar_dados_devolve_apenas_os_campos_alterados() -> None:
    empresa = cadastrar()

    alteracoes = empresa.alterar_dados(
        razao_social="Empresa Y Ltda", nome_fantasia="Empresa X", cnpj=OUTRO_CNPJ
    )

    assert alteracoes == {
        "razao_social": {"anterior": "Empresa X Ltda", "novo": "Empresa Y Ltda"},
        "cnpj": {"anterior": "12345678000195", "novo": "11222333000181"},
    }
    assert empresa.razao_social == "Empresa Y Ltda"
    assert empresa.cnpj == OUTRO_CNPJ


def test_alterar_dados_sem_mudanca_devolve_nada_alterado() -> None:
    empresa = cadastrar()

    alteracoes = empresa.alterar_dados(
        razao_social=" Empresa X Ltda ", nome_fantasia="Empresa X", cnpj=CNPJ
    )

    assert alteracoes == {}


def test_alterar_dados_valida_como_no_cadastro() -> None:
    empresa = cadastrar()

    with pytest.raises(RazaoSocialInvalida):
        empresa.alterar_dados(razao_social="", nome_fantasia=None, cnpj=CNPJ)

    assert empresa.razao_social == "Empresa X Ltda"


def test_empresa_desativada_pode_ter_os_dados_alterados() -> None:
    empresa = cadastrar()
    empresa.desativar()

    empresa.alterar_dados(razao_social="Empresa Y Ltda", nome_fantasia=None, cnpj=CNPJ)

    assert empresa.razao_social == "Empresa Y Ltda"
    assert empresa.situacao is SituacaoDaEmpresa.DESATIVADA
