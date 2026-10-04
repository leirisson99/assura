"""Duas remoções simultâneas não deixam a empresa sem administrador (CS-001).

Usa duas conexões de verdade, com dados confirmados e apagados no fim, e um histórico em memória:
registros no histórico real não podem ser apagados.
"""

import threading
from collections.abc import Iterator
from uuid import UUID, uuid7

import pytest
from sqlalchemy import Engine, delete, insert
from sqlalchemy.orm import Session

from assura.compartilhado.dominio.pagina import Pagina
from assura.historico import FiltroDoHistorico, RegistrarAcao, RegistroDeHistorico
from assura.identidade import (
    Permissoes,
    RemoverAdministrador,
    UltimoAdministradorNaoPodeSerRemovido,
    criar_empresas,
    criar_vinculos,
)
from assura.identidade.infraestrutura.tabela import tabela_empresa, tabela_usuario, tabela_vinculo
from tests.apoio import gerar_cnpj_valido
from tests.identidade.apoio import SOLICITANTE

TEMPO_MAXIMO_DE_ESPERA_EM_SEGUNDOS = 10


class HistoricoEmMemoria:
    def __init__(self) -> None:
        self.registros: list[RegistroDeHistorico] = []

    def adicionar(self, registro: RegistroDeHistorico) -> None:
        self.registros.append(registro)

    def consultar(self, filtro: FiltroDoHistorico, pagina: Pagina) -> list[RegistroDeHistorico]:
        return self.registros


@pytest.fixture
def dois_administradores(motor_de_teste: Engine) -> Iterator[tuple[UUID, UUID]]:
    empresa_id = uuid7()
    usuarios_ids = [uuid7(), uuid7()]
    vinculos_ids = [uuid7(), uuid7()]
    with Session(motor_de_teste) as sessao:
        sessao.execute(
            insert(tabela_empresa).values(
                id=empresa_id, razao_social="Simultânea", cnpj=gerar_cnpj_valido(), situacao="ativa"
            )
        )
        for usuario_id, vinculo_id in zip(usuarios_ids, vinculos_ids, strict=True):
            sessao.execute(
                insert(tabela_usuario).values(
                    id=usuario_id, nome="Adm", email=f"{usuario_id}@x.com", situacao="ativo"
                )
            )
            sessao.execute(
                insert(tabela_vinculo).values(
                    id=vinculo_id,
                    usuario_id=usuario_id,
                    empresa_id=empresa_id,
                    situacao="ativo",
                    administrador_da_empresa=True,
                )
            )
        sessao.commit()
    yield vinculos_ids[0], vinculos_ids[1]
    with Session(motor_de_teste) as sessao:
        sessao.execute(delete(tabela_vinculo).where(tabela_vinculo.c.empresa_id == empresa_id))
        sessao.execute(delete(tabela_usuario).where(tabela_usuario.c.id.in_(usuarios_ids)))
        sessao.execute(delete(tabela_empresa).where(tabela_empresa.c.id == empresa_id))
        sessao.commit()


def remover(sessao: Session, vinculo_id: UUID) -> None:
    vinculos = criar_vinculos(sessao)
    RemoverAdministrador(
        vinculos,
        Permissoes(vinculos, criar_empresas(sessao)),
        RegistrarAcao(HistoricoEmMemoria()),
    ).executar(solicitante=SOLICITANTE, vinculo_id=vinculo_id)


def test_remocoes_simultaneas_deixam_um_administrador(
    motor_de_teste: Engine, dois_administradores: tuple[UUID, UUID]
) -> None:
    primeiro, segundo = dois_administradores
    erros_da_segunda: list[Exception] = []

    with Session(motor_de_teste) as sessao_da_primeira:
        remover(sessao_da_primeira, primeiro)  # bloqueia os administradores até o commit

        def remover_o_segundo() -> None:
            with Session(motor_de_teste) as sessao_da_segunda:
                try:
                    remover(sessao_da_segunda, segundo)
                    sessao_da_segunda.commit()
                except Exception as erro:
                    erros_da_segunda.append(erro)

        segunda = threading.Thread(target=remover_o_segundo)
        segunda.start()
        segunda.join(timeout=0.5)
        assert segunda.is_alive(), "a segunda remoção deveria esperar o bloqueio da primeira"

        sessao_da_primeira.commit()

    segunda.join(timeout=TEMPO_MAXIMO_DE_ESPERA_EM_SEGUNDOS)
    assert [type(erro) for erro in erros_da_segunda] == [UltimoAdministradorNaoPodeSerRemovido]
    with Session(motor_de_teste) as sessao:
        assert criar_vinculos(sessao).obter(segundo).administrador_da_empresa
