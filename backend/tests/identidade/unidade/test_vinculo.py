from uuid import uuid4

import pytest

from assura.identidade.dominio.erros import VinculoJaAtivo, VinculoJaDesativado
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
