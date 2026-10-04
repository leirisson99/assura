from collections.abc import Callable, Mapping

from sqlalchemy import Engine, Executable, MetaData, create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

# Nomes previsíveis para restrições e índices, para que as migrações possam referenciá-los.
CONVENCAO_DE_NOMES = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadados = MetaData(naming_convention=CONVENCAO_DE_NOMES)


def criar_motor(url_banco_de_dados: str) -> Engine:
    return create_engine(url_banco_de_dados)


def criar_fabrica_de_sessoes(motor: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=motor)


def ler_restricao_violada(erro: IntegrityError) -> str | None:
    diagnostico = getattr(erro.orig, "diag", None)
    return getattr(diagnostico, "constraint_name", None)


def executar_traduzindo_restricoes(
    sessao: Session,
    comando: Executable,
    erros_por_restricao: Mapping[str, Callable[[], Exception]],
) -> None:
    """Executa num savepoint e troca a violação de uma restrição conhecida por erro do domínio.

    O savepoint mantém a transação de quem chama utilizável depois da recusa do banco.
    """
    try:
        with sessao.begin_nested():
            sessao.execute(comando)
    except IntegrityError as erro:
        criar_erro_do_dominio = erros_por_restricao.get(ler_restricao_violada(erro) or "")
        if criar_erro_do_dominio is None:
            raise
        raise criar_erro_do_dominio() from erro
