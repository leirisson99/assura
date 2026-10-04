from uuid import uuid4

import pytest

from assura.identidade.dominio.erros import (
    VinculoDesativadoNaoPodeSerAdministrador,
    VinculoJaAtivo,
    VinculoJaDesativado,
    VinculoJaEAdministrador,
    VinculoNaoEAdministrador,
)
from assura.identidade.dominio.vinculo import SituacaoDoVinculo, Vinculo


def criar_vinculo() -> Vinculo:
    return Vinculo.criar(usuario_id=uuid4(), empresa_id=uuid4())


def test_vinculo_nasce_ativo() -> None:
    assert criar_vinculo().situacao is SituacaoDoVinculo.ATIVO


def test_vinculo_ativo_pode_ser_desativado() -> None:
    vinculo = criar_vinculo()

    vinculo.desativar()

    assert vinculo.situacao is SituacaoDoVinculo.DESATIVADO


def test_vinculo_desativado_pode_ser_reativado() -> None:
    vinculo = criar_vinculo()
    vinculo.desativar()

    vinculo.reativar()

    assert vinculo.situacao is SituacaoDoVinculo.ATIVO


def test_vinculo_desativado_nao_pode_ser_desativado_de_novo() -> None:
    vinculo = criar_vinculo()
    vinculo.desativar()

    with pytest.raises(VinculoJaDesativado):
        vinculo.desativar()


def test_vinculo_ativo_nao_pode_ser_reativado() -> None:
    with pytest.raises(VinculoJaAtivo):
        criar_vinculo().reativar()


def test_vinculo_nasce_sem_o_papel_de_administrador() -> None:
    vinculo = criar_vinculo()

    assert not vinculo.administrador_da_empresa
    assert not vinculo.e_administrador_ativo


def test_vinculo_ativo_pode_ser_tornado_administrador() -> None:
    vinculo = criar_vinculo()

    vinculo.tornar_administrador()

    assert vinculo.administrador_da_empresa
    assert vinculo.e_administrador_ativo


def test_administrador_com_vinculo_desativado_nao_e_administrador_ativo() -> None:
    vinculo = criar_vinculo()
    vinculo.tornar_administrador()

    vinculo.desativar()

    assert vinculo.administrador_da_empresa
    assert not vinculo.e_administrador_ativo


def test_vinculo_desativado_nao_pode_ser_tornado_administrador() -> None:
    vinculo = criar_vinculo()
    vinculo.desativar()

    with pytest.raises(VinculoDesativadoNaoPodeSerAdministrador):
        vinculo.tornar_administrador()


def test_quem_ja_e_administrador_nao_e_tornado_de_novo() -> None:
    vinculo = criar_vinculo()
    vinculo.tornar_administrador()

    with pytest.raises(VinculoJaEAdministrador):
        vinculo.tornar_administrador()


def test_remover_administrador_tira_o_papel() -> None:
    vinculo = criar_vinculo()
    vinculo.tornar_administrador()

    vinculo.remover_administrador()

    assert not vinculo.administrador_da_empresa


def test_remover_administrador_de_quem_nao_e_e_recusado() -> None:
    with pytest.raises(VinculoNaoEAdministrador):
        criar_vinculo().remover_administrador()
