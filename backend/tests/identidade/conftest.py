import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao, criar_historico
from assura.identidade import Empresas, criar_empresas
from tests.identidade.apoio import INSTANTE


@pytest.fixture
def empresas(sessao: Session) -> Empresas:
    return criar_empresas(sessao)


@pytest.fixture
def registrar_acao(sessao: Session) -> RegistrarAcao:
    return RegistrarAcao(criar_historico(sessao), relogio=lambda: INSTANTE)
