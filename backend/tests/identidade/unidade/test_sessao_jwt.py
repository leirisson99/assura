from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from assura.identidade.dominio.erros import SessaoInvalida
from assura.identidade.infraestrutura.sessao_jwt import EmissorDeSessaoJwt

CHAVE = "chave-de-teste-com-pelo-menos-32-bytes!!"
AGORA = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)


def criar_emissor(chave: str = CHAVE, agora: datetime = AGORA) -> EmissorDeSessaoJwt:
    return EmissorDeSessaoJwt(chave=chave, validade=timedelta(hours=8), relogio=lambda: agora)


def test_sessao_emitida_identifica_o_usuario_e_expira_em_8_horas() -> None:
    usuario_id = uuid4()

    sessao = criar_emissor().emitir(usuario_id)

    assert sessao.expira_em == AGORA + timedelta(hours=8)
    assert criar_emissor().ler(sessao.token) == usuario_id


def test_sessao_vencida_e_recusada() -> None:
    sessao = criar_emissor().emitir(uuid4())
    depois_de_vencer = AGORA + timedelta(hours=8, seconds=1)

    with pytest.raises(SessaoInvalida):
        criar_emissor(agora=depois_de_vencer).ler(sessao.token)


def test_sessao_assinada_com_outra_chave_e_recusada() -> None:
    sessao = criar_emissor(chave="outra-chave-tambem-com-32-bytes-ou-mais").emitir(uuid4())

    with pytest.raises(SessaoInvalida):
        criar_emissor().ler(sessao.token)


@pytest.mark.parametrize("token", ["", "abc", "a.b.c"])
def test_token_malformado_e_recusado(token: str) -> None:
    with pytest.raises(SessaoInvalida):
        criar_emissor().ler(token)


def test_token_adulterado_e_recusado() -> None:
    cabecalho, conteudo, assinatura = criar_emissor().emitir(uuid4()).token.split(".")
    adulterado = f"{cabecalho}.{conteudo}x.{assinatura}"

    with pytest.raises(SessaoInvalida):
        criar_emissor().ler(adulterado)
