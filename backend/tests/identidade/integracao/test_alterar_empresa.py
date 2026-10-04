from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao
from assura.identidade import (
    AlterarEmpresa,
    CnpjJaCadastrado,
    DesativarEmpresa,
    Empresa,
    EmpresaNaoEncontrada,
    Empresas,
    SituacaoDaEmpresa,
)
from tests.identidade.apoio import (
    AUTOR,
    OUTRO_CNPJ_NUMERICO,
    SOLICITANTE,
    cadastrar_empresa,
    ler_historico_da_empresa,
)


def alterar(
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    empresa: Empresa,
    **alteracoes: str | None,
) -> Empresa:
    dados: dict[str, str | None] = {
        "razao_social": empresa.razao_social,
        "nome_fantasia": empresa.nome_fantasia,
        "cnpj": empresa.cnpj.valor,
    }
    dados.update(alteracoes)
    return AlterarEmpresa(empresas, registrar_acao).executar(
        solicitante=SOLICITANTE,
        empresa_id=empresa.id,
        razao_social=dados["razao_social"] or "",
        nome_fantasia=dados["nome_fantasia"],
        cnpj=dados["cnpj"] or "",
    )


def test_alteracao_fica_gravada(empresas: Empresas, registrar_acao: RegistrarAcao) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    alterar(empresas, registrar_acao, empresa, razao_social="Empresa Y Ltda", nome_fantasia=None)

    gravada = empresas.obter(empresa.id)
    assert gravada.razao_social == "Empresa Y Ltda"
    assert gravada.nome_fantasia is None


def test_historico_registra_apenas_os_campos_alterados(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    alterar(empresas, registrar_acao, empresa, razao_social="Empresa Y Ltda")

    _, alteracao = ler_historico_da_empresa(sessao, empresa.id)
    assert alteracao.tipo_de_acao == "empresa_alterada"
    assert alteracao.autor == AUTOR
    assert alteracao.empresa_id == empresa.id
    assert alteracao.detalhes == {
        "razao_social": {"anterior": "Empresa X Ltda", "novo": "Empresa Y Ltda"}
    }


def test_alteracao_sem_mudanca_nao_gera_registro(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    alterar(empresas, registrar_acao, empresa, cnpj=empresa.cnpj.formatado)

    assert len(ler_historico_da_empresa(sessao, empresa.id)) == 1


def test_cnpj_de_outra_empresa_e_recusado_e_empresa_continua_igual(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)
    cadastrar_empresa(empresas, registrar_acao, cnpj=OUTRO_CNPJ_NUMERICO)

    with pytest.raises(CnpjJaCadastrado):
        alterar(empresas, registrar_acao, empresa, razao_social="Nova", cnpj=OUTRO_CNPJ_NUMERICO)

    assert empresas.obter(empresa.id).razao_social == "Empresa X Ltda"
    assert len(ler_historico_da_empresa(sessao, empresa.id)) == 1


def test_empresa_desativada_pode_ser_alterada(
    empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)
    DesativarEmpresa(empresas, registrar_acao).executar(
        solicitante=SOLICITANTE, empresa_id=empresa.id
    )
    desativada = empresas.obter(empresa.id)

    alterar(empresas, registrar_acao, desativada, razao_social="Empresa Y Ltda")

    gravada = empresas.obter(empresa.id)
    assert gravada.razao_social == "Empresa Y Ltda"
    assert gravada.situacao is SituacaoDaEmpresa.DESATIVADA


def test_empresa_inexistente_e_recusada(empresas: Empresas, registrar_acao: RegistrarAcao) -> None:
    with pytest.raises(EmpresaNaoEncontrada):
        AlterarEmpresa(empresas, registrar_acao).executar(
            solicitante=SOLICITANTE,
            empresa_id=uuid4(),
            razao_social="Empresa",
            nome_fantasia=None,
            cnpj=OUTRO_CNPJ_NUMERICO,
        )
