from uuid import uuid4

import pytest

from assura.historico import Pagina, RegistrarAcao
from assura.identidade import (
    ConsultarEmpresas,
    DesativarEmpresa,
    Empresa,
    EmpresaNaoEncontrada,
    Empresas,
    SituacaoDaEmpresa,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from tests.apoio import gerar_cnpj_valido
from tests.identidade.apoio import SOLICITANTE, cadastrar_empresa


def cadastrar_varias(
    empresas: Empresas, registrar_acao: RegistrarAcao, razoes_sociais: list[str]
) -> list[Empresa]:
    return [
        cadastrar_empresa(
            empresas, registrar_acao, razao_social=razao_social, cnpj=gerar_cnpj_valido()
        )
        for razao_social in razoes_sociais
    ]


def razoes_sociais(empresas: list[Empresa]) -> list[str]:
    return [empresa.razao_social for empresa in empresas]


def test_obter_devolve_os_dados_da_empresa(
    permissoes: Permissoes, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    encontrada = ConsultarEmpresas(empresas, permissoes).obter(
        solicitante=SOLICITANTE, empresa_id=empresa.id
    )

    assert encontrada == empresa


def test_obter_empresa_inexistente_e_recusado(permissoes: Permissoes, empresas: Empresas) -> None:
    with pytest.raises(EmpresaNaoEncontrada):
        ConsultarEmpresas(empresas, permissoes).obter(solicitante=SOLICITANTE, empresa_id=uuid4())


def test_listar_sem_filtro_traz_todas_em_ordem_alfabetica(
    permissoes: Permissoes, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    cadastradas = cadastrar_varias(empresas, registrar_acao, ["Gama", "alfa", "Beta"])
    DesativarEmpresa(empresas, registrar_acao).executar(
        solicitante=SOLICITANTE, empresa_id=cadastradas[0].id
    )

    listadas = ConsultarEmpresas(empresas, permissoes).listar(solicitante=SOLICITANTE)

    assert razoes_sociais(listadas) == ["alfa", "Beta", "Gama"]


@pytest.mark.parametrize(
    ("situacao", "esperadas"),
    [(SituacaoDaEmpresa.ATIVA, ["alfa", "Beta"]), (SituacaoDaEmpresa.DESATIVADA, ["Gama"])],
)
def test_listar_filtra_por_situacao(
    permissoes: Permissoes,
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    situacao: SituacaoDaEmpresa,
    esperadas: list[str],
) -> None:
    cadastradas = cadastrar_varias(empresas, registrar_acao, ["Gama", "alfa", "Beta"])
    DesativarEmpresa(empresas, registrar_acao).executar(
        solicitante=SOLICITANTE, empresa_id=cadastradas[0].id
    )

    listadas = ConsultarEmpresas(empresas, permissoes).listar(
        solicitante=SOLICITANTE, situacao=situacao
    )

    assert razoes_sociais(listadas) == esperadas


def test_listar_em_paginas(
    permissoes: Permissoes, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    cadastrar_varias(empresas, registrar_acao, ["A", "B", "C", "D", "E"])
    consultar = ConsultarEmpresas(empresas, permissoes)

    paginas = [
        razoes_sociais(
            consultar.listar(solicitante=SOLICITANTE, pagina=Pagina(numero=numero, tamanho=2))
        )
        for numero in (1, 2, 3)
    ]

    assert paginas == [["A", "B"], ["C", "D"], ["E"]]


def test_listar_sem_empresas_devolve_lista_vazia(
    permissoes: Permissoes, empresas: Empresas
) -> None:
    assert ConsultarEmpresas(empresas, permissoes).listar(solicitante=SOLICITANTE) == []
