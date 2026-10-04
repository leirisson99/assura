from collections.abc import Iterator
from functools import cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session, sessionmaker

from assura.compartilhado.infraestrutura.banco import criar_fabrica_de_sessoes, criar_motor
from assura.configuracao import configuracao


@cache
def obter_fabrica_de_sessoes() -> sessionmaker[Session]:
    return criar_fabrica_de_sessoes(criar_motor(configuracao.url_banco_de_dados))


def obter_sessao_do_banco() -> Iterator[Session]:
    """Uma sessão por requisição. O endpoint confirma com commit; o que não for confirmado é
    desfeito ao fechar a sessão."""
    with obter_fabrica_de_sessoes()() as sessao:
        yield sessao


SessaoDoBanco = Annotated[Session, Depends(obter_sessao_do_banco)]
