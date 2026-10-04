from collections.abc import Callable
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from assura.historico import (
    Autor,
    ObjetoAfetado,
    RegistrarAcao,
    TipoDeAcao,
    criar_historico,
)
from assura.historico.infraestrutura.tabela import tabela_registro_de_historico

INSTANTE = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)
OBJETO_DE_EXEMPLO = ObjetoAfetado(tipo="exemplo", identificador="1")


class FalhaNaAcaoDeExemplo(Exception):
    pass


def criar_registrar_acao(sessao: Session) -> RegistrarAcao:
    return RegistrarAcao(criar_historico(sessao), relogio=lambda: INSTANTE)


def contar_registros(sessao: Session) -> int:
    return sessao.scalar(select(func.count()).select_from(tabela_registro_de_historico)) or 0


def criar_tabela_de_acao_de_exemplo(sessao: Session) -> None:
    sessao.execute(text("CREATE TEMP TABLE acao_de_exemplo (descricao text NOT NULL)"))


def gravar_acao_de_exemplo(sessao: Session) -> None:
    sessao.execute(text("INSERT INTO acao_de_exemplo VALUES ('mudança de negócio')"))


def contar_acoes_de_exemplo(sessao: Session) -> int:
    return sessao.scalar(text("SELECT count(*) FROM acao_de_exemplo")) or 0


def test_acao_registrada_fica_gravada_com_todos_os_dados(
    sessao: Session, criar_empresa: Callable[[], UUID]
) -> None:
    empresa_id = criar_empresa()
    usuario_id = uuid4()

    criar_registrar_acao(sessao).executar(
        autor=Autor.usuario(usuario_id),
        tipo_de_acao=TipoDeAcao.EMPRESA_CADASTRADA,
        objeto=OBJETO_DE_EXEMPLO,
        empresa_id=empresa_id,
        detalhes={"nome": "Empresa X", "ativa": True},
    )

    linha = sessao.execute(select(tabela_registro_de_historico)).mappings().one()
    assert linha["autor_tipo"] == "usuario"
    assert linha["autor_usuario_id"] == usuario_id
    assert linha["tipo_de_acao"] == "empresa_cadastrada"
    assert linha["objeto_tipo"] == "exemplo"
    assert linha["objeto_id"] == "1"
    assert linha["empresa_id"] == empresa_id
    assert linha["registrado_em"] == INSTANTE
    assert linha["detalhes"] == {"nome": "Empresa X", "ativa": True}


def test_acao_fora_de_empresa_fica_gravada_sem_empresa(sessao: Session) -> None:
    criar_registrar_acao(sessao).executar(
        autor=Autor.sistema(),
        tipo_de_acao=TipoDeAcao.EMPRESA_CADASTRADA,
        objeto=OBJETO_DE_EXEMPLO,
        empresa_id=None,
    )

    linha = sessao.execute(select(tabela_registro_de_historico)).mappings().one()
    assert linha["empresa_id"] is None
    assert linha["autor_tipo"] == "sistema"
    assert linha["autor_usuario_id"] is None
    assert linha["detalhes"] == {}


def test_falha_da_acao_depois_do_registro_desfaz_a_acao_e_o_registro(sessao: Session) -> None:
    criar_tabela_de_acao_de_exemplo(sessao)

    with pytest.raises(FalhaNaAcaoDeExemplo), sessao.begin_nested():
        gravar_acao_de_exemplo(sessao)
        criar_registrar_acao(sessao).executar(
            autor=Autor.sistema(),
            tipo_de_acao=TipoDeAcao.EMPRESA_CADASTRADA,
            objeto=OBJETO_DE_EXEMPLO,
            empresa_id=None,
        )
        raise FalhaNaAcaoDeExemplo

    assert contar_acoes_de_exemplo(sessao) == 0
    assert contar_registros(sessao) == 0


def test_falha_ao_gravar_o_registro_desfaz_a_acao_de_negocio(sessao: Session) -> None:
    criar_tabela_de_acao_de_exemplo(sessao)
    historico = criar_historico(sessao)
    registro_ja_gravado = RegistrarAcao(historico, relogio=lambda: INSTANTE).executar(
        autor=Autor.sistema(),
        tipo_de_acao=TipoDeAcao.EMPRESA_CADASTRADA,
        objeto=OBJETO_DE_EXEMPLO,
        empresa_id=None,
    )

    # Gravar de novo o mesmo registro viola a chave primária: o banco recusa o histórico.
    with pytest.raises(IntegrityError), sessao.begin_nested():
        gravar_acao_de_exemplo(sessao)
        historico.adicionar(registro_ja_gravado)

    assert contar_acoes_de_exemplo(sessao) == 0
    assert contar_registros(sessao) == 1


def test_registrar_acao_nao_confirma_a_transacao_de_quem_chama(sessao: Session) -> None:
    sessao.begin_nested()
    criar_registrar_acao(sessao).executar(
        autor=Autor.sistema(),
        tipo_de_acao=TipoDeAcao.EMPRESA_CADASTRADA,
        objeto=OBJETO_DE_EXEMPLO,
        empresa_id=None,
    )
    sessao.rollback()

    assert contar_registros(sessao) == 0


def test_registro_com_empresa_inexistente_e_recusado(sessao: Session) -> None:
    with pytest.raises(IntegrityError), sessao.begin_nested():
        criar_registrar_acao(sessao).executar(
            autor=Autor.sistema(),
            tipo_de_acao=TipoDeAcao.EMPRESA_CADASTRADA,
            objeto=OBJETO_DE_EXEMPLO,
            empresa_id=uuid4(),
        )

    assert contar_registros(sessao) == 0
