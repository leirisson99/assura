"""Rotas do histórico. Ficam em identidade porque quem pode consultar depende dos papéis."""

from dataclasses import replace
from datetime import datetime
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from assura.historico import (
    Autor,
    ConsultarHistorico,
    FiltroDoHistorico,
    ObjetoAfetado,
    RegistroDeHistorico,
    SolicitanteDaConsulta,
    TipoDeAcao,
    criar_historico,
)
from assura.identidade.aplicacao.permissoes import exigir_administrador_do_sistema
from assura.identidade.infraestrutura.dependencias_http import (
    PaginaPedida,
    RepositoriosDaRequisicao,
    Solicitante,
)

roteador_de_historico = APIRouter(tags=["histórico"])


class RegistroResposta(BaseModel):
    id: UUID
    autor_tipo: str
    autor_usuario_id: UUID | None
    tipo_de_acao: str
    objeto_tipo: str
    objeto_id: str
    empresa_id: UUID | None
    registrado_em: datetime
    detalhes: dict[str, Any]

    @classmethod
    def de(cls, registro: RegistroDeHistorico) -> RegistroResposta:
        return cls(
            id=registro.id,
            autor_tipo=registro.autor.tipo,
            autor_usuario_id=registro.autor.usuario_id,
            tipo_de_acao=registro.tipo_de_acao,
            objeto_tipo=registro.objeto.tipo,
            objeto_id=registro.objeto.identificador,
            empresa_id=registro.empresa_id,
            registrado_em=registro.registrado_em,
            detalhes=registro.detalhes,
        )


def ler_filtro(
    inicio: datetime | None = None,
    fim: datetime | None = None,
    tipo_de_acao: TipoDeAcao | None = None,
    objeto_tipo: str | None = None,
    objeto_id: str | None = None,
    autor_usuario_id: UUID | None = None,
) -> FiltroDoHistorico:
    objeto = (
        ObjetoAfetado(tipo=objeto_tipo, identificador=objeto_id)
        if objeto_tipo is not None and objeto_id is not None
        else None
    )
    autor = Autor.usuario(autor_usuario_id) if autor_usuario_id is not None else None
    return FiltroDoHistorico(
        inicio=inicio, fim=fim, tipo_de_acao=tipo_de_acao, objeto=objeto, autor=autor
    )


FiltroPedido = Annotated[FiltroDoHistorico, Depends(ler_filtro)]


def consultar(
    repositorios: RepositoriosDaRequisicao,
    solicitante_da_consulta: SolicitanteDaConsulta,
    filtro: FiltroDoHistorico,
    pagina: PaginaPedida,
) -> list[RegistroResposta]:
    registros = ConsultarHistorico(criar_historico(repositorios.sessao)).executar(
        solicitante=solicitante_da_consulta, filtro=filtro, pagina=pagina
    )
    return [RegistroResposta.de(registro) for registro in registros]


@roteador_de_historico.get("/historico")
def consultar_historico(
    solicitante: Solicitante,
    repositorios: RepositoriosDaRequisicao,
    filtro: FiltroPedido,
    pagina: PaginaPedida,
    empresa_id: UUID | None = None,
) -> list[RegistroResposta]:
    exigir_administrador_do_sistema(solicitante)
    return consultar(
        repositorios,
        SolicitanteDaConsulta.administrador_do_sistema(),
        replace(filtro, empresa_id=empresa_id),
        pagina,
    )


@roteador_de_historico.get("/empresas/{empresa_id}/historico")
def consultar_historico_da_empresa(
    empresa_id: UUID,
    solicitante: Solicitante,
    repositorios: RepositoriosDaRequisicao,
    filtro: FiltroPedido,
    pagina: PaginaPedida,
) -> list[RegistroResposta]:
    repositorios.permissoes.exigir_administrador_da_empresa(solicitante, empresa_id)
    return consultar(
        repositorios,
        SolicitanteDaConsulta.administrador_da_empresa(empresa_id),
        replace(filtro, empresa_id=empresa_id),
        pagina,
    )
