from sqlalchemy import ColumnElement, RowMapping, insert, select
from sqlalchemy.orm import Session

from assura.historico.aplicacao.portas import HistoricoDeAcoes
from assura.historico.dominio.consulta import FiltroDoHistorico, Pagina
from assura.historico.dominio.registro_de_historico import (
    Autor,
    ObjetoAfetado,
    RegistroDeHistorico,
    TipoDeAutor,
)
from assura.historico.infraestrutura.tabela import tabela_registro_de_historico

colunas = tabela_registro_de_historico.c


class HistoricoDeAcoesSqlAlchemy:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, registro: RegistroDeHistorico) -> None:
        self._sessao.execute(
            insert(tabela_registro_de_historico).values(
                id=registro.id,
                autor_tipo=str(registro.autor.tipo),
                autor_usuario_id=registro.autor.usuario_id,
                tipo_de_acao=registro.tipo_de_acao,
                objeto_tipo=registro.objeto.tipo,
                objeto_id=registro.objeto.identificador,
                empresa_id=registro.empresa_id,
                registrado_em=registro.registrado_em,
                detalhes=registro.detalhes,
            )
        )

    def consultar(self, filtro: FiltroDoHistorico, pagina: Pagina) -> list[RegistroDeHistorico]:
        consulta = (
            select(tabela_registro_de_historico)
            .where(*montar_condicoes(filtro))
            .order_by(colunas.registrado_em.desc(), colunas.id.desc())
            .limit(pagina.tamanho)
            .offset(pagina.deslocamento)
        )
        linhas = self._sessao.execute(consulta).mappings()
        return [converter_em_registro(linha) for linha in linhas]


def montar_condicoes(filtro: FiltroDoHistorico) -> list[ColumnElement[bool]]:
    condicoes: list[ColumnElement[bool]] = []
    if filtro.empresa_id is not None:
        condicoes.append(colunas.empresa_id == filtro.empresa_id)
    if filtro.inicio is not None:
        condicoes.append(colunas.registrado_em >= filtro.inicio)
    if filtro.fim is not None:
        condicoes.append(colunas.registrado_em <= filtro.fim)
    if filtro.autor is not None:
        condicoes.append(colunas.autor_tipo == str(filtro.autor.tipo))
        if filtro.autor.usuario_id is not None:
            condicoes.append(colunas.autor_usuario_id == filtro.autor.usuario_id)
    if filtro.tipo_de_acao is not None:
        condicoes.append(colunas.tipo_de_acao == str(filtro.tipo_de_acao))
    if filtro.objeto is not None:
        condicoes.append(colunas.objeto_tipo == filtro.objeto.tipo)
        condicoes.append(colunas.objeto_id == filtro.objeto.identificador)
    return condicoes


def converter_em_registro(linha: RowMapping) -> RegistroDeHistorico:
    return RegistroDeHistorico(
        id=linha["id"],
        autor=Autor(tipo=TipoDeAutor(linha["autor_tipo"]), usuario_id=linha["autor_usuario_id"]),
        tipo_de_acao=linha["tipo_de_acao"],
        objeto=ObjetoAfetado(tipo=linha["objeto_tipo"], identificador=linha["objeto_id"]),
        empresa_id=linha["empresa_id"],
        registrado_em=linha["registrado_em"],
        detalhes=linha["detalhes"],
    )


def criar_historico(sessao: Session) -> HistoricoDeAcoes:
    return HistoricoDeAcoesSqlAlchemy(sessao)
