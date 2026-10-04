import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao, criar_historico
from assura.identidade import (
    Empresas,
    Usuarios,
    Vinculos,
    criar_empresas,
    criar_usuarios,
    criar_vinculos,
)
from tests.identidade.apoio import INSTANTE


@pytest.fixture
def empresas(sessao: Session) -> Empresas:
    return criar_empresas(sessao)


@pytest.fixture
def registrar_acao(sessao: Session) -> RegistrarAcao:
    return RegistrarAcao(criar_historico(sessao), relogio=lambda: INSTANTE)


@pytest.fixture
def usuarios(sessao: Session) -> Usuarios:
    return criar_usuarios(sessao)


@pytest.fixture
def vinculos(sessao: Session) -> Vinculos:
    return criar_vinculos(sessao)
