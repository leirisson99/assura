from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from assura.historico import (
    Autor,
    ConsultaAOutraEmpresaNaoPermitida,
    ConsultarHistorico,
    FiltroDoHistorico,
    ObjetoAfetado,
    Pagina,
    RegistrarAcao,
    RegistroDeHistorico,
    SolicitanteDaConsulta,
    TipoDeAcao,
    criar_historico,
)
from tests.historico.tipos_de_teste import TipoDeAcaoDeTeste

PRIMEIRO_DIA = datetime(2026, 10, 1, 9, 0, tzinfo=UTC)


def registrar(
    sessao: Session,
    *,
    empresa_id: UUID | None,
    registrado_em: datetime = PRIMEIRO_DIA,
    autor: Autor | None = None,
    tipo_de_acao: TipoDeAcao = TipoDeAcaoDeTeste.ACAO_DE_EXEMPLO,
    objeto: ObjetoAfetado | None = None,
) -> RegistroDeHistorico:
    return RegistrarAcao(criar_historico(sessao), relogio=lambda: registrado_em).executar(
        autor=autor or Autor.sistema(),
        tipo_de_acao=tipo_de_acao,
        objeto=objeto or ObjetoAfetado(tipo="exemplo", identificador="1"),
        empresa_id=empresa_id,
    )


def consultar(
    sessao: Session,
    solicitante: SolicitanteDaConsulta,
    filtro: FiltroDoHistorico | None = None,
    pagina: Pagina | None = None,
) -> list[RegistroDeHistorico]:
    return ConsultarHistorico(criar_historico(sessao)).executar(
        solicitante=solicitante,
        filtro=filtro or FiltroDoHistorico(),
        pagina=pagina or Pagina(),
    )


def identificadores(registros: list[RegistroDeHistorico]) -> list[UUID]:
    return [registro.id for registro in registros]


def test_administrador_da_empresa_ve_apenas_registros_da_propria_empresa(sessao: Session) -> None:
    empresa_a, empresa_b = uuid4(), uuid4()
    registro_de_a = registrar(sessao, empresa_id=empresa_a)
    registrar(sessao, empresa_id=empresa_b)
    registrar(sessao, empresa_id=None)

    resultado = consultar(sessao, SolicitanteDaConsulta.administrador_da_empresa(empresa_a))

    assert identificadores(resultado) == [registro_de_a.id]


def test_administrador_da_empresa_nao_consulta_outra_empresa(sessao: Session) -> None:
    empresa_a, empresa_b = uuid4(), uuid4()
    registrar(sessao, empresa_id=empresa_b)

    with pytest.raises(ConsultaAOutraEmpresaNaoPermitida):
        consultar(
            sessao,
            SolicitanteDaConsulta.administrador_da_empresa(empresa_a),
            FiltroDoHistorico(empresa_id=empresa_b),
        )


def test_administrador_do_sistema_ve_todas_as_empresas_e_registros_sem_empresa(
    sessao: Session,
) -> None:
    registros = [
        registrar(sessao, empresa_id=uuid4()),
        registrar(sessao, empresa_id=uuid4()),
        registrar(sessao, empresa_id=None),
    ]

    resultado = consultar(sessao, SolicitanteDaConsulta.administrador_do_sistema())

    assert set(identificadores(resultado)) == set(identificadores(registros))


def test_administrador_do_sistema_pode_restringir_a_uma_empresa(sessao: Session) -> None:
    empresa_a = uuid4()
    registro_de_a = registrar(sessao, empresa_id=empresa_a)
    registrar(sessao, empresa_id=uuid4())

    resultado = consultar(
        sessao,
        SolicitanteDaConsulta.administrador_do_sistema(),
        FiltroDoHistorico(empresa_id=empresa_a),
    )

    assert identificadores(resultado) == [registro_de_a.id]


def test_resultado_vem_do_mais_recente_para_o_mais_antigo(sessao: Session) -> None:
    empresa_id = uuid4()
    antigo = registrar(sessao, empresa_id=empresa_id, registrado_em=PRIMEIRO_DIA)
    recente = registrar(sessao, empresa_id=empresa_id, registrado_em=PRIMEIRO_DIA + timedelta(1))
    mesmo_instante = registrar(
        sessao, empresa_id=empresa_id, registrado_em=PRIMEIRO_DIA + timedelta(1)
    )

    resultado = consultar(sessao, SolicitanteDaConsulta.administrador_da_empresa(empresa_id))

    assert identificadores(resultado) == [mesmo_instante.id, recente.id, antigo.id]


def test_filtro_por_periodo_inclui_os_limites(sessao: Session) -> None:
    empresa_id = uuid4()
    dias = [PRIMEIRO_DIA + timedelta(days=dia) for dia in range(4)]
    registros = [registrar(sessao, empresa_id=empresa_id, registrado_em=dia) for dia in dias]

    resultado = consultar(
        sessao,
        SolicitanteDaConsulta.administrador_da_empresa(empresa_id),
        FiltroDoHistorico(inicio=dias[1], fim=dias[2]),
    )

    assert identificadores(resultado) == [registros[2].id, registros[1].id]


def test_filtro_por_autor(sessao: Session) -> None:
    empresa_id = uuid4()
    autor = Autor.usuario(uuid4())
    do_autor = registrar(sessao, empresa_id=empresa_id, autor=autor)
    registrar(sessao, empresa_id=empresa_id, autor=Autor.usuario(uuid4()))
    registrar(sessao, empresa_id=empresa_id, autor=Autor.sistema())

    resultado = consultar(
        sessao,
        SolicitanteDaConsulta.administrador_da_empresa(empresa_id),
        FiltroDoHistorico(autor=autor),
    )

    assert identificadores(resultado) == [do_autor.id]


def test_filtro_por_autor_sistema(sessao: Session) -> None:
    empresa_id = uuid4()
    do_sistema = registrar(sessao, empresa_id=empresa_id, autor=Autor.sistema())
    registrar(sessao, empresa_id=empresa_id, autor=Autor.usuario(uuid4()))

    resultado = consultar(
        sessao,
        SolicitanteDaConsulta.administrador_da_empresa(empresa_id),
        FiltroDoHistorico(autor=Autor.sistema()),
    )

    assert identificadores(resultado) == [do_sistema.id]


def test_filtro_por_tipo_de_acao(sessao: Session) -> None:
    empresa_id = uuid4()
    outra_acao = registrar(
        sessao, empresa_id=empresa_id, tipo_de_acao=TipoDeAcaoDeTeste.OUTRA_ACAO_DE_EXEMPLO
    )
    registrar(sessao, empresa_id=empresa_id, tipo_de_acao=TipoDeAcaoDeTeste.ACAO_DE_EXEMPLO)

    resultado = consultar(
        sessao,
        SolicitanteDaConsulta.administrador_da_empresa(empresa_id),
        FiltroDoHistorico(tipo_de_acao=TipoDeAcaoDeTeste.OUTRA_ACAO_DE_EXEMPLO),
    )

    assert identificadores(resultado) == [outra_acao.id]


def test_filtro_por_objeto(sessao: Session) -> None:
    empresa_id = uuid4()
    objeto = ObjetoAfetado(tipo="exemplo", identificador="procurado")
    do_objeto = registrar(sessao, empresa_id=empresa_id, objeto=objeto)
    registrar(sessao, empresa_id=empresa_id, objeto=ObjetoAfetado("exemplo", "outro"))
    registrar(sessao, empresa_id=empresa_id, objeto=ObjetoAfetado("outro_tipo", "procurado"))

    resultado = consultar(
        sessao,
        SolicitanteDaConsulta.administrador_da_empresa(empresa_id),
        FiltroDoHistorico(objeto=objeto),
    )

    assert identificadores(resultado) == [do_objeto.id]


def test_filtros_combinados_exigem_todos(sessao: Session) -> None:
    empresa_id = uuid4()
    autor = Autor.usuario(uuid4())
    procurado = registrar(
        sessao,
        empresa_id=empresa_id,
        autor=autor,
        tipo_de_acao=TipoDeAcaoDeTeste.OUTRA_ACAO_DE_EXEMPLO,
    )
    registrar(sessao, empresa_id=empresa_id, autor=autor)
    registrar(sessao, empresa_id=empresa_id, tipo_de_acao=TipoDeAcaoDeTeste.OUTRA_ACAO_DE_EXEMPLO)

    resultado = consultar(
        sessao,
        SolicitanteDaConsulta.administrador_da_empresa(empresa_id),
        FiltroDoHistorico(autor=autor, tipo_de_acao=TipoDeAcaoDeTeste.OUTRA_ACAO_DE_EXEMPLO),
    )

    assert identificadores(resultado) == [procurado.id]


def test_paginacao_devolve_cada_pagina_sem_repetir_registros(sessao: Session) -> None:
    empresa_id = uuid4()
    registros = [
        registrar(sessao, empresa_id=empresa_id, registrado_em=PRIMEIRO_DIA + timedelta(hours=hora))
        for hora in range(5)
    ]
    do_mais_recente = list(reversed(identificadores(registros)))
    solicitante = SolicitanteDaConsulta.administrador_da_empresa(empresa_id)

    paginas = [
        identificadores(consultar(sessao, solicitante, pagina=Pagina(numero=numero, tamanho=2)))
        for numero in (1, 2, 3)
    ]

    assert paginas == [do_mais_recente[0:2], do_mais_recente[2:4], do_mais_recente[4:5]]


def test_consulta_sem_resultados_devolve_lista_vazia(sessao: Session) -> None:
    resultado = consultar(sessao, SolicitanteDaConsulta.administrador_da_empresa(uuid4()))

    assert resultado == []


def test_registro_consultado_e_igual_ao_registrado(sessao: Session) -> None:
    empresa_id = uuid4()
    registrado = RegistrarAcao(criar_historico(sessao), relogio=lambda: PRIMEIRO_DIA).executar(
        autor=Autor.usuario(uuid4()),
        tipo_de_acao=TipoDeAcaoDeTeste.ACAO_DE_EXEMPLO,
        objeto=ObjetoAfetado(tipo="exemplo", identificador="1"),
        empresa_id=empresa_id,
        detalhes={"nome": "Empresa X", "itens": [1, 2]},
    )

    resultado = consultar(sessao, SolicitanteDaConsulta.administrador_da_empresa(empresa_id))

    assert resultado == [registrado]
