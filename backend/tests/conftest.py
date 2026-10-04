from collections.abc import Callable, Iterator
from pathlib import Path
from uuid import UUID, uuid7

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, insert, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.orm import Session

from assura.configuracao import configuracao
from assura.identidade.infraestrutura.tabela import tabela_empresa
from tests.apoio import gerar_cnpj_valido

CAMINHO_DO_ALEMBIC_INI = Path(__file__).resolve().parent.parent / "alembic.ini"


def criar_banco_se_nao_existir(url: URL) -> None:
    motor_administrativo = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with motor_administrativo.connect() as conexao:
        banco_existe = conexao.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :nome"), {"nome": url.database}
        )
        if not banco_existe:
            conexao.execute(text(f'CREATE DATABASE "{url.database}"'))
    motor_administrativo.dispose()


def criar_configuracao_do_alembic(url: URL) -> Config:
    configuracao_do_alembic = Config(str(CAMINHO_DO_ALEMBIC_INI))
    configuracao_do_alembic.set_main_option(
        "sqlalchemy.url", url.render_as_string(hide_password=False)
    )
    return configuracao_do_alembic


@pytest.fixture(scope="session")
def url_do_banco_de_teste() -> URL:
    return make_url(configuracao.url_banco_de_dados_de_teste)


@pytest.fixture(scope="session")
def configuracao_do_alembic(url_do_banco_de_teste: URL) -> Config:
    return criar_configuracao_do_alembic(url_do_banco_de_teste)


@pytest.fixture(scope="session")
def motor_de_teste(url_do_banco_de_teste: URL, configuracao_do_alembic: Config) -> Iterator[Engine]:
    criar_banco_se_nao_existir(url_do_banco_de_teste)
    command.upgrade(configuracao_do_alembic, "head")
    motor = create_engine(url_do_banco_de_teste)
    yield motor
    motor.dispose()


@pytest.fixture
def sessao(motor_de_teste: Engine) -> Iterator[Session]:
    """Sessão dentro de uma transação desfeita no fim do teste.

    Os commits da sessão viram savepoints; nada fica gravado, e o histórico (que não aceita
    exclusão) não precisa ser limpo.
    """
    with motor_de_teste.connect() as conexao:
        transacao = conexao.begin()
        sessao_de_teste = Session(bind=conexao, join_transaction_mode="create_savepoint")
        yield sessao_de_teste
        sessao_de_teste.close()
        transacao.rollback()


@pytest.fixture
def criar_empresa(sessao: Session) -> Callable[[], UUID]:
    """Grava uma empresa direto na tabela, sem registro de histórico, e devolve o id."""

    def criar() -> UUID:
        empresa_id = uuid7()
        sessao.execute(
            insert(tabela_empresa).values(
                id=empresa_id,
                razao_social=f"Empresa {empresa_id}",
                cnpj=gerar_cnpj_valido(),
                situacao="ativa",
            )
        )
        return empresa_id

    return criar
