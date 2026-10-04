from collections.abc import Iterator, Mapping
from enum import IntEnum
from functools import cache
from typing import Annotated

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker

from assura.compartilhado.dominio.pagina import PaginaInvalida
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


class CategoriaDeErro(IntEnum):
    """Como um erro de domínio aparece para quem chama a API."""

    NAO_AUTENTICADO = status.HTTP_401_UNAUTHORIZED
    SEM_PERMISSAO = status.HTTP_403_FORBIDDEN
    NAO_ENCONTRADO = status.HTTP_404_NOT_FOUND
    CONFLITO_COM_O_ESTADO = status.HTTP_409_CONFLICT
    DADOS_INVALIDOS = status.HTTP_422_UNPROCESSABLE_CONTENT


def registrar_traducao_de_erros(
    aplicacao: FastAPI,
    erro_base: type[Exception],
    categorias: Mapping[type[Exception], CategoriaDeErro],
) -> None:
    """Responde aos erros de um contexto com o código da categoria; sem categoria, dados
    inválidos. A mensagem do erro vai em `detail`."""

    def responder(_: Request, erro: Exception) -> JSONResponse:
        categoria = next(
            (categorias[tipo] for tipo in type(erro).__mro__ if tipo in categorias),
            CategoriaDeErro.DADOS_INVALIDOS,
        )
        return JSONResponse(status_code=categoria, content={"detail": str(erro)})

    aplicacao.add_exception_handler(erro_base, responder)


def registrar_traducao_de_erros_compartilhados(aplicacao: FastAPI) -> None:
    registrar_traducao_de_erros(aplicacao, PaginaInvalida, {})
