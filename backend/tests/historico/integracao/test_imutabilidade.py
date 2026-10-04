from datetime import UTC, datetime

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from assura.historico import Autor, ObjetoAfetado, RegistrarAcao, criar_historico
from assura.historico.infraestrutura.historico_sqlalchemy import HistoricoDeAcoesSqlAlchemy
from assura.historico.infraestrutura.tabela import tabela_registro_de_historico
from tests.historico.tipos_de_teste import TipoDeAcaoDeTeste

MENSAGEM_DE_HISTORICO_IMUTAVEL = "o histórico de ações não pode ser alterado nem excluído"

COMANDOS_QUE_ALTERAM_O_HISTORICO = [
    "UPDATE registro_de_historico SET objeto_id = 'adulterado'",
    "DELETE FROM registro_de_historico",
    "TRUNCATE registro_de_historico",
]


def gravar_registro(sessao: Session) -> None:
    RegistrarAcao(
        criar_historico(sessao), relogio=lambda: datetime(2026, 10, 4, tzinfo=UTC)
    ).executar(
        autor=Autor.sistema(),
        tipo_de_acao=TipoDeAcaoDeTeste.ACAO_DE_EXEMPLO,
        objeto=ObjetoAfetado(tipo="exemplo", identificador="original"),
        empresa_id=None,
    )


@pytest.mark.parametrize("comando", COMANDOS_QUE_ALTERAM_O_HISTORICO)
def test_banco_rejeita_comando_direto_que_altera_o_historico(sessao: Session, comando: str) -> None:
    gravar_registro(sessao)

    with pytest.raises(DBAPIError, match=MENSAGEM_DE_HISTORICO_IMUTAVEL), sessao.begin_nested():
        sessao.execute(text(comando))

    linha = sessao.execute(select(tabela_registro_de_historico)).mappings().one()
    assert linha["objeto_id"] == "original"


def test_historico_nao_oferece_operacao_de_alterar_ou_excluir() -> None:
    operacoes_publicas = {
        nome for nome in dir(HistoricoDeAcoesSqlAlchemy) if not nome.startswith("_")
    }

    assert operacoes_publicas == {"adicionar", "consultar"}
