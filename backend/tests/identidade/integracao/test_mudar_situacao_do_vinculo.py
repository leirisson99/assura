from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao
from assura.identidade import (
    DesativarVinculo,
    Empresas,
    ReativarVinculo,
    SituacaoDoUsuario,
    SituacaoDoVinculo,
    Usuarios,
    VincularUsuario,
    Vinculo,
    VinculoJaAtivo,
    VinculoJaDesativado,
    VinculoNaoEncontrado,
    Vinculos,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from tests.apoio import gerar_cnpj_valido
from tests.identidade.apoio import (
    SOLICITANTE,
    cadastrar_empresa,
    cadastrar_usuario,
    ler_historico_do_objeto,
)


@pytest.fixture
def vinculos_do_usuario(
    usuarios: Usuarios, empresas: Empresas, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> tuple[Vinculo, Vinculo]:
    """Um usuário vinculado a duas empresas."""
    usuario = cadastrar_usuario(usuarios, registrar_acao)
    vincular = VincularUsuario(usuarios, empresas, vinculos, registrar_acao)
    vinculo_a, vinculo_b = (
        vincular.executar(
            solicitante=SOLICITANTE,
            usuario_id=usuario.id,
            empresa_id=cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido()).id,
        )
        for _ in range(2)
    )
    return vinculo_a, vinculo_b


def test_desativar_vinculo_nao_afeta_o_usuario_nem_o_outro_vinculo(
    permissoes: Permissoes,
    sessao: Session,
    usuarios: Usuarios,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
    vinculos_do_usuario: tuple[Vinculo, Vinculo],
) -> None:
    vinculo_a, vinculo_b = vinculos_do_usuario

    DesativarVinculo(vinculos, permissoes, registrar_acao).executar(
        solicitante=SOLICITANTE, vinculo_id=vinculo_a.id
    )

    assert vinculos.obter(vinculo_a.id).situacao is SituacaoDoVinculo.DESATIVADO
    assert vinculos.obter(vinculo_b.id).situacao is SituacaoDoVinculo.ATIVO
    assert usuarios.obter(vinculo_a.usuario_id).situacao is SituacaoDoUsuario.ATIVO
    _, desativacao = ler_historico_do_objeto(sessao, "vinculo", vinculo_a.id)
    assert desativacao.tipo_de_acao == "vinculo_desativado"
    assert desativacao.empresa_id == vinculo_a.empresa_id
    assert desativacao.detalhes == {"usuario_id": str(vinculo_a.usuario_id)}


def test_reativar_vinculo_grava_a_situacao_e_o_historico(
    permissoes: Permissoes,
    sessao: Session,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
    vinculos_do_usuario: tuple[Vinculo, Vinculo],
) -> None:
    vinculo, _ = vinculos_do_usuario
    DesativarVinculo(vinculos, permissoes, registrar_acao).executar(
        solicitante=SOLICITANTE, vinculo_id=vinculo.id
    )

    ReativarVinculo(vinculos, permissoes, registrar_acao).executar(
        solicitante=SOLICITANTE, vinculo_id=vinculo.id
    )

    assert vinculos.obter(vinculo.id).situacao is SituacaoDoVinculo.ATIVO
    tipos = [
        registro.tipo_de_acao for registro in ler_historico_do_objeto(sessao, "vinculo", vinculo.id)
    ]
    assert tipos == ["usuario_vinculado", "vinculo_desativado", "vinculo_reativado"]


def test_desativar_de_novo_e_recusado_sem_registro(
    permissoes: Permissoes,
    sessao: Session,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
    vinculos_do_usuario: tuple[Vinculo, Vinculo],
) -> None:
    vinculo, _ = vinculos_do_usuario
    desativar = DesativarVinculo(vinculos, permissoes, registrar_acao)
    desativar.executar(solicitante=SOLICITANTE, vinculo_id=vinculo.id)

    with pytest.raises(VinculoJaDesativado):
        desativar.executar(solicitante=SOLICITANTE, vinculo_id=vinculo.id)

    assert len(ler_historico_do_objeto(sessao, "vinculo", vinculo.id)) == 2


def test_reativar_vinculo_ativo_e_recusado_sem_registro(
    permissoes: Permissoes,
    sessao: Session,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
    vinculos_do_usuario: tuple[Vinculo, Vinculo],
) -> None:
    vinculo, _ = vinculos_do_usuario

    with pytest.raises(VinculoJaAtivo):
        ReativarVinculo(vinculos, permissoes, registrar_acao).executar(
            solicitante=SOLICITANTE, vinculo_id=vinculo.id
        )

    assert len(ler_historico_do_objeto(sessao, "vinculo", vinculo.id)) == 1


@pytest.mark.parametrize("caso_de_uso", [DesativarVinculo, ReativarVinculo])
def test_vinculo_inexistente_e_recusado(
    permissoes: Permissoes,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
    caso_de_uso: type[DesativarVinculo] | type[ReativarVinculo],
) -> None:
    with pytest.raises(VinculoNaoEncontrado):
        caso_de_uso(vinculos, permissoes, registrar_acao).executar(
            solicitante=SOLICITANTE, vinculo_id=uuid4()
        )
