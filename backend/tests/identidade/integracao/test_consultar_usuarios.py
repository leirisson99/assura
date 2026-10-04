from uuid import UUID, uuid4

import pytest

from assura.historico import Pagina, RegistrarAcao
from assura.identidade import (
    ConsultarUsuarios,
    DesativarVinculo,
    Empresas,
    SituacaoDoVinculo,
    UsuarioDaEmpresa,
    UsuarioNaoEncontrado,
    Usuarios,
    VincularUsuario,
    Vinculos,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from tests.apoio import gerar_cnpj_valido
from tests.identidade.apoio import SOLICITANTE, cadastrar_empresa, cadastrar_usuario


def nomes(usuarios_da_empresa: list[UsuarioDaEmpresa]) -> list[str]:
    return [usuario_da_empresa.usuario.nome for usuario_da_empresa in usuarios_da_empresa]


@pytest.fixture
def duas_empresas(
    permissoes: Permissoes,
    usuarios: Usuarios,
    empresas: Empresas,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
) -> tuple[UUID, UUID]:
    """Empresa A com Carla, ana (vínculo desativado) e Bruno; empresa B com Diego."""
    empresa_a = cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido()).id
    empresa_b = cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido()).id
    vincular = VincularUsuario(usuarios, empresas, vinculos, registrar_acao)
    for nome, empresa_id in [
        ("Carla", empresa_a),
        ("ana", empresa_a),
        ("Bruno", empresa_a),
        ("Diego", empresa_b),
    ]:
        usuario = cadastrar_usuario(usuarios, registrar_acao, nome=nome, email=f"{nome}@x.com")
        vinculo = vincular.executar(
            solicitante=SOLICITANTE, usuario_id=usuario.id, empresa_id=empresa_id
        )
        if nome == "ana":
            DesativarVinculo(vinculos, permissoes, registrar_acao).executar(
                solicitante=SOLICITANTE, vinculo_id=vinculo.id
            )
    return empresa_a, empresa_b


def test_obter_devolve_o_usuario(
    permissoes: Permissoes, usuarios: Usuarios, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)

    assert (
        ConsultarUsuarios(usuarios, vinculos, permissoes).obter(
            solicitante=SOLICITANTE, usuario_id=usuario.id
        )
        == usuario
    )


def test_obter_usuario_inexistente_e_recusado(
    permissoes: Permissoes, usuarios: Usuarios, vinculos: Vinculos
) -> None:
    with pytest.raises(UsuarioNaoEncontrado):
        ConsultarUsuarios(usuarios, vinculos, permissoes).obter(
            solicitante=SOLICITANTE, usuario_id=uuid4()
        )


def test_listar_traz_so_os_usuarios_da_empresa_em_ordem_de_nome(
    permissoes: Permissoes, usuarios: Usuarios, vinculos: Vinculos, duas_empresas: tuple[UUID, UUID]
) -> None:
    empresa_a, empresa_b = duas_empresas
    consultar = ConsultarUsuarios(usuarios, vinculos, permissoes)

    da_empresa_a = consultar.listar_da_empresa(solicitante=SOLICITANTE, empresa_id=empresa_a)

    assert nomes(da_empresa_a) == ["ana", "Bruno", "Carla"]
    assert all(item.vinculo.empresa_id == empresa_a for item in da_empresa_a)
    assert nomes(consultar.listar_da_empresa(solicitante=SOLICITANTE, empresa_id=empresa_b)) == [
        "Diego"
    ]


@pytest.mark.parametrize(
    ("situacao", "esperados"),
    [(SituacaoDoVinculo.ATIVO, ["Bruno", "Carla"]), (SituacaoDoVinculo.DESATIVADO, ["ana"])],
)
def test_listar_filtra_pela_situacao_do_vinculo(
    permissoes: Permissoes,
    usuarios: Usuarios,
    vinculos: Vinculos,
    duas_empresas: tuple[UUID, UUID],
    situacao: SituacaoDoVinculo,
    esperados: list[str],
) -> None:
    empresa_a, _ = duas_empresas

    listados = ConsultarUsuarios(usuarios, vinculos, permissoes).listar_da_empresa(
        solicitante=SOLICITANTE, empresa_id=empresa_a, situacao=situacao
    )

    assert nomes(listados) == esperados


def test_listar_em_paginas(
    permissoes: Permissoes, usuarios: Usuarios, vinculos: Vinculos, duas_empresas: tuple[UUID, UUID]
) -> None:
    empresa_a, _ = duas_empresas
    consultar = ConsultarUsuarios(usuarios, vinculos, permissoes)

    paginas = [
        nomes(
            consultar.listar_da_empresa(
                solicitante=SOLICITANTE,
                empresa_id=empresa_a,
                pagina=Pagina(numero=numero, tamanho=2),
            )
        )
        for numero in (1, 2)
    ]

    assert paginas == [["ana", "Bruno"], ["Carla"]]


def test_listar_empresa_sem_usuarios_devolve_lista_vazia(
    permissoes: Permissoes, usuarios: Usuarios, vinculos: Vinculos
) -> None:
    assert (
        ConsultarUsuarios(usuarios, vinculos, permissoes).listar_da_empresa(
            solicitante=SOLICITANTE, empresa_id=uuid4()
        )
        == []
    )
