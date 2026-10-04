from sqlalchemy import Engine, MetaData, create_engine
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
