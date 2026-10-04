from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from assura.historico.dominio.erros import (
    AutorInvalido,
    ObjetoAfetadoInvalido,
    TipoDeAcaoDesconhecido,
)
from assura.historico.dominio.registro_de_historico import (
    Autor,
    ObjetoAfetado,
    RegistroDeHistorico,
    TipoDeAcao,
    TipoDeAutor,
)

INSTANTE = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)


def criar_registro(**alteracoes: Any) -> RegistroDeHistorico:
    argumentos: dict[str, Any] = {
        "autor": Autor.sistema(),
        "tipo_de_acao": TipoDeAcao.EMPRESA_CADASTRADA,
        "objeto": ObjetoAfetado(tipo="exemplo", identificador="1"),
        "empresa_id": None,
        "registrado_em": INSTANTE,
        "detalhes": {},
    }
    argumentos.update(alteracoes)
    return RegistroDeHistorico.criar(**argumentos)


def test_autor_usuario_guarda_o_identificador_do_usuario() -> None:
    usuario_id = uuid4()

    autor = Autor.usuario(usuario_id)

    assert autor.tipo is TipoDeAutor.USUARIO
    assert autor.usuario_id == usuario_id


def test_autor_sistema_nao_tem_identificador_de_usuario() -> None:
    autor = Autor.sistema()

    assert autor.tipo is TipoDeAutor.SISTEMA
    assert autor.usuario_id is None


def test_autor_usuario_sem_identificador_e_recusado() -> None:
    with pytest.raises(AutorInvalido):
        Autor(tipo=TipoDeAutor.USUARIO)


def test_autor_sistema_com_identificador_e_recusado() -> None:
    with pytest.raises(AutorInvalido):
        Autor(tipo=TipoDeAutor.SISTEMA, usuario_id=uuid4())


@pytest.mark.parametrize(("tipo", "identificador"), [("", "1"), ("exemplo", ""), ("  ", "1")])
def test_objeto_afetado_sem_tipo_ou_identificador_e_recusado(tipo: str, identificador: str) -> None:
    with pytest.raises(ObjetoAfetadoInvalido):
        ObjetoAfetado(tipo=tipo, identificador=identificador)


def test_tipo_de_acao_fora_da_lista_e_recusado() -> None:
    with pytest.raises(TipoDeAcaoDesconhecido):
        criar_registro(tipo_de_acao="acao_inventada")


def test_registro_guarda_todos_os_dados_da_acao() -> None:
    empresa_id = uuid4()
    autor = Autor.usuario(uuid4())

    registro = criar_registro(autor=autor, empresa_id=empresa_id, detalhes={"nome": "Empresa X"})

    assert registro.autor == autor
    assert registro.tipo_de_acao == "empresa_cadastrada"
    assert registro.objeto == ObjetoAfetado(tipo="exemplo", identificador="1")
    assert registro.empresa_id == empresa_id
    assert registro.registrado_em == INSTANTE
    assert registro.detalhes == {"nome": "Empresa X"}


def test_registro_nao_pode_ser_alterado_depois_de_criado() -> None:
    registro = criar_registro()

    with pytest.raises(AttributeError):
        registro.tipo_de_acao = "outra"  # type: ignore[misc]


def test_identificadores_criados_em_sequencia_sao_crescentes() -> None:
    registros = [criar_registro() for _ in range(50)]

    identificadores = [registro.id for registro in registros]

    assert identificadores == sorted(identificadores)
