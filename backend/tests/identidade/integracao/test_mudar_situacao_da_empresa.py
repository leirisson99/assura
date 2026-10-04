from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao
from assura.identidade import (
    DesativarEmpresa,
    EmpresaJaAtiva,
    EmpresaJaDesativada,
    EmpresaNaoEncontrada,
    Empresas,
    ReativarEmpresa,
    SituacaoDaEmpresa,
)
from tests.identidade.apoio import AUTOR, cadastrar_empresa, ler_historico_da_empresa


def test_desativar_grava_a_situacao_e_o_historico(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    DesativarEmpresa(empresas, registrar_acao).executar(autor=AUTOR, empresa_id=empresa.id)

    gravada = empresas.obter(empresa.id)
    assert gravada.situacao is SituacaoDaEmpresa.DESATIVADA
    assert gravada.razao_social == "Empresa X Ltda"
    _, desativacao = ler_historico_da_empresa(sessao, empresa.id)
    assert desativacao.tipo_de_acao == "empresa_desativada"
    assert desativacao.autor == AUTOR
    assert desativacao.detalhes == {}


def test_reativar_grava_a_situacao_e_o_historico(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)
    DesativarEmpresa(empresas, registrar_acao).executar(autor=AUTOR, empresa_id=empresa.id)

    ReativarEmpresa(empresas, registrar_acao).executar(autor=AUTOR, empresa_id=empresa.id)

    assert empresas.obter(empresa.id).situacao is SituacaoDaEmpresa.ATIVA
    tipos = [registro.tipo_de_acao for registro in ler_historico_da_empresa(sessao, empresa.id)]
    assert tipos == ["empresa_cadastrada", "empresa_desativada", "empresa_reativada"]


def test_desativar_de_novo_e_recusado_sem_registro(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)
    desativar = DesativarEmpresa(empresas, registrar_acao)
    desativar.executar(autor=AUTOR, empresa_id=empresa.id)

    with pytest.raises(EmpresaJaDesativada):
        desativar.executar(autor=AUTOR, empresa_id=empresa.id)

    assert len(ler_historico_da_empresa(sessao, empresa.id)) == 2


def test_reativar_empresa_ativa_e_recusado_sem_registro(
    sessao: Session, empresas: Empresas, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    with pytest.raises(EmpresaJaAtiva):
        ReativarEmpresa(empresas, registrar_acao).executar(autor=AUTOR, empresa_id=empresa.id)

    assert len(ler_historico_da_empresa(sessao, empresa.id)) == 1


@pytest.mark.parametrize("caso_de_uso", [DesativarEmpresa, ReativarEmpresa])
def test_empresa_inexistente_e_recusada(
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    caso_de_uso: type[DesativarEmpresa] | type[ReativarEmpresa],
) -> None:
    with pytest.raises(EmpresaNaoEncontrada):
        caso_de_uso(empresas, registrar_acao).executar(autor=AUTOR, empresa_id=uuid4())
