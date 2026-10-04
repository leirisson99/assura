from datetime import timedelta

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
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.infraestrutura.resumo_de_senha_argon2 import GeradorDeResumoArgon2
from assura.identidade.infraestrutura.sessao_jwt import EmissorDeSessaoJwt
from tests.apoio import GERADOR_DE_RESUMO_RAPIDO
from tests.identidade.apoio import CHAVE_DE_SESSAO_DE_TESTE, INSTANTE


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


@pytest.fixture(scope="session")
def gerador_de_resumo() -> GeradorDeResumoArgon2:
    return GeradorDeResumoArgon2(GERADOR_DE_RESUMO_RAPIDO)


@pytest.fixture
def emissor_de_sessao() -> EmissorDeSessaoJwt:
    return EmissorDeSessaoJwt(chave=CHAVE_DE_SESSAO_DE_TESTE, validade=timedelta(hours=8))


@pytest.fixture
def permissoes(vinculos: Vinculos, empresas: Empresas) -> Permissoes:
    return Permissoes(vinculos, empresas)
