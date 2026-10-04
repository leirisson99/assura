from datetime import UTC, datetime
from uuid import uuid4

import pytest

from assura.compartilhado.dominio.pagina import (
    TAMANHO_DE_PAGINA_MAXIMO,
    TAMANHO_DE_PAGINA_PADRAO,
    Pagina,
    PaginaInvalida,
)
from assura.historico.dominio.consulta import FiltroDoHistorico, SolicitanteDaConsulta
from assura.historico.dominio.erros import (
    ConsultaAOutraEmpresaNaoPermitida,
    PeriodoInvalido,
)


def test_administrador_da_empresa_consulta_a_propria_empresa_sem_informar_qual() -> None:
    empresa_id = uuid4()
    solicitante = SolicitanteDaConsulta.administrador_da_empresa(empresa_id)

    assert solicitante.definir_empresa_da_consulta(None) == empresa_id


def test_administrador_da_empresa_consulta_a_propria_empresa_informada() -> None:
    empresa_id = uuid4()
    solicitante = SolicitanteDaConsulta.administrador_da_empresa(empresa_id)

    assert solicitante.definir_empresa_da_consulta(empresa_id) == empresa_id


def test_administrador_da_empresa_nao_consulta_outra_empresa() -> None:
    solicitante = SolicitanteDaConsulta.administrador_da_empresa(uuid4())

    with pytest.raises(ConsultaAOutraEmpresaNaoPermitida):
        solicitante.definir_empresa_da_consulta(uuid4())


def test_administrador_do_sistema_consulta_todas_as_empresas() -> None:
    solicitante = SolicitanteDaConsulta.administrador_do_sistema()

    assert solicitante.definir_empresa_da_consulta(None) is None


def test_administrador_do_sistema_consulta_uma_empresa_escolhida() -> None:
    empresa_id = uuid4()
    solicitante = SolicitanteDaConsulta.administrador_do_sistema()

    assert solicitante.definir_empresa_da_consulta(empresa_id) == empresa_id


def test_periodo_com_inicio_depois_do_fim_e_recusado() -> None:
    with pytest.raises(PeriodoInvalido):
        FiltroDoHistorico(
            inicio=datetime(2026, 10, 5, tzinfo=UTC), fim=datetime(2026, 10, 4, tzinfo=UTC)
        )


def test_pagina_padrao_e_a_primeira_com_tamanho_padrao() -> None:
    pagina = Pagina()

    assert pagina.numero == 1
    assert pagina.tamanho == TAMANHO_DE_PAGINA_PADRAO
    assert pagina.deslocamento == 0


def test_deslocamento_da_terceira_pagina_pula_as_duas_anteriores() -> None:
    assert Pagina(numero=3, tamanho=10).deslocamento == 20


@pytest.mark.parametrize(
    ("numero", "tamanho"), [(0, 10), (1, 0), (1, TAMANHO_DE_PAGINA_MAXIMO + 1)]
)
def test_pagina_fora_dos_limites_e_recusada(numero: int, tamanho: int) -> None:
    with pytest.raises(PaginaInvalida):
        Pagina(numero=numero, tamanho=tamanho)
