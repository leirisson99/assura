import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from assura.historico import Autor, RegistrarAcao
from assura.identidade import (
    CadastrarEmpresa,
    CnpjInvalido,
    CnpjJaCadastrado,
    DesativarEmpresa,
    Empresa,
    Empresas,
    RazaoSocialInvalida,
    SituacaoDaEmpresa,
)
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.infraestrutura.tabela import tabela_empresa
from tests.identidade.apoio import (
    AUTOR,
    CNPJ_ALFANUMERICO,
    CNPJ_NUMERICO,
    INSTANTE,
    cadastrar_empresa,
    ler_historico_da_empresa,
)


def contar_empresas(sessao: Session) -> int:
    return sessao.scalar(select(func.count()).select_from(tabela_empresa)) or 0


def test_empresa_cadastrada_fica_gravada_e_ativa(
    empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    gravada = empresas.obter(empresa.id)
    assert gravada.razao_social == "Empresa X Ltda"
    assert gravada.nome_fantasia == "Empresa X"
    assert gravada.cnpj.valor == "12345678000195"
    assert gravada.situacao is SituacaoDaEmpresa.ATIVA


def test_cnpj_alfanumerico_e_aceito(empresas: Empresas, registrar_acao: RegistrarAcao) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao, cnpj=CNPJ_ALFANUMERICO)

    assert empresas.obter(empresa.id).cnpj.valor == "12ABC34501DE35"


def test_cadastro_fica_no_historico_da_propria_empresa(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    [registro] = ler_historico_da_empresa(sessao, empresa.id)
    assert registro.tipo_de_acao == "empresa_cadastrada"
    assert registro.autor == AUTOR
    assert registro.empresa_id == empresa.id
    assert registro.registrado_em == INSTANTE
    assert registro.detalhes == {
        "razao_social": "Empresa X Ltda",
        "nome_fantasia": "Empresa X",
        "cnpj": "12345678000195",
    }


def test_cnpj_ja_cadastrado_com_outra_mascara_e_recusado(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    cadastrar_empresa(empresas, registrar_acao, cnpj=CNPJ_NUMERICO)

    with pytest.raises(CnpjJaCadastrado):
        cadastrar_empresa(empresas, registrar_acao, cnpj="12345678000195")

    assert contar_empresas(sessao) == 1


def test_cnpj_de_empresa_desativada_nao_pode_ser_reusado(
    empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)
    DesativarEmpresa(empresas, registrar_acao).executar(autor=AUTOR, empresa_id=empresa.id)

    with pytest.raises(CnpjJaCadastrado):
        cadastrar_empresa(empresas, registrar_acao)


@pytest.mark.parametrize(
    ("dados_invalidos", "erro"),
    [
        ({"cnpj": "12.345.678/0001-96"}, CnpjInvalido),
        ({"razao_social": "  "}, RazaoSocialInvalida),
    ],
)
def test_dados_invalidos_nao_gravam_empresa_nem_historico(
    sessao: Session,
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    dados_invalidos: dict[str, str],
    erro: type[Exception],
) -> None:
    with pytest.raises(erro):
        cadastrar_empresa(empresas, registrar_acao, **dados_invalidos)

    assert contar_empresas(sessao) == 0


def test_restricao_do_banco_recusa_cnpj_repetido_que_passou_pela_verificacao(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    # Simula dois cadastros simultâneos: o segundo grava sem ter visto o primeiro.
    cadastrar_empresa(empresas, registrar_acao)
    concorrente = Empresa.cadastrar(
        razao_social="Concorrente Ltda", nome_fantasia=None, cnpj=Cnpj.criar(CNPJ_NUMERICO)
    )

    with pytest.raises(CnpjJaCadastrado):
        empresas.adicionar(concorrente)

    assert contar_empresas(sessao) == 1


def test_autor_sistema_tambem_pode_cadastrar(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = CadastrarEmpresa(empresas, registrar_acao).executar(
        autor=Autor.sistema(), razao_social="Empresa X", nome_fantasia=None, cnpj=CNPJ_NUMERICO
    )

    [registro] = ler_historico_da_empresa(sessao, empresa.id)
    assert registro.autor == Autor.sistema()
    assert registro.detalhes["nome_fantasia"] is None
