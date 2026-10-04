from collections.abc import Callable
from uuid import UUID

import pytest

from assura.identidade import (
    Empresas,
    PermissaoNegada,
    UsuarioAutenticado,
    Vinculo,
    Vinculos,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from tests.identidade.apoio import SOLICITANTE

CriarRegistro = Callable[[], UUID]


def solicitante_comum(usuario_id: UUID) -> UsuarioAutenticado:
    return UsuarioAutenticado(id=usuario_id, administrador_do_sistema=False, senha_provisoria=False)


def vincular(
    vinculos: Vinculos, usuario_id: UUID, empresa_id: UUID, *, administrador: bool = False
) -> Vinculo:
    vinculo = Vinculo.criar(usuario_id=usuario_id, empresa_id=empresa_id)
    if administrador:
        vinculo.tornar_administrador()
    vinculos.adicionar(vinculo)
    return vinculo


def test_administrador_do_sistema_pode_tudo(
    permissoes: Permissoes, criar_empresa: CriarRegistro, criar_usuario: CriarRegistro
) -> None:
    permissoes.exigir_administrador_do_sistema(SOLICITANTE)
    permissoes.exigir_administrador_da_empresa(SOLICITANTE, criar_empresa())
    permissoes.exigir_pode_ver_usuario(SOLICITANTE, criar_usuario())


def test_usuario_comum_nao_e_administrador_do_sistema(
    permissoes: Permissoes, criar_usuario: CriarRegistro
) -> None:
    with pytest.raises(PermissaoNegada):
        permissoes.exigir_administrador_do_sistema(solicitante_comum(criar_usuario()))


def test_administrador_ativo_da_empresa_administra_so_a_propria(
    permissoes: Permissoes,
    vinculos: Vinculos,
    criar_empresa: CriarRegistro,
    criar_usuario: CriarRegistro,
) -> None:
    empresa_a, empresa_b = criar_empresa(), criar_empresa()
    administrador = criar_usuario()
    vincular(vinculos, administrador, empresa_a, administrador=True)
    vincular(vinculos, administrador, empresa_b)

    permissoes.exigir_administrador_da_empresa(solicitante_comum(administrador), empresa_a)
    with pytest.raises(PermissaoNegada):
        permissoes.exigir_administrador_da_empresa(solicitante_comum(administrador), empresa_b)


def test_administrador_com_vinculo_desativado_perde_a_permissao(
    permissoes: Permissoes,
    vinculos: Vinculos,
    criar_empresa: CriarRegistro,
    criar_usuario: CriarRegistro,
) -> None:
    empresa, administrador = criar_empresa(), criar_usuario()
    vinculo = vincular(vinculos, administrador, empresa, administrador=True)
    vinculo.desativar()
    vinculos.atualizar(vinculo)

    with pytest.raises(PermissaoNegada):
        permissoes.exigir_administrador_da_empresa(solicitante_comum(administrador), empresa)


def test_administrador_de_empresa_desativada_perde_a_permissao(
    permissoes: Permissoes,
    vinculos: Vinculos,
    empresas: Empresas,
    criar_empresa: CriarRegistro,
    criar_usuario: CriarRegistro,
) -> None:
    empresa, administrador = criar_empresa(), criar_usuario()
    vincular(vinculos, administrador, empresa, administrador=True)
    empresa_desativada = empresas.obter(empresa)
    empresa_desativada.desativar()
    empresas.atualizar(empresa_desativada)

    with pytest.raises(PermissaoNegada):
        permissoes.exigir_administrador_da_empresa(solicitante_comum(administrador), empresa)


def test_ver_usuario_o_proprio_e_administrador_de_empresa_em_comum(
    permissoes: Permissoes,
    vinculos: Vinculos,
    criar_empresa: CriarRegistro,
    criar_usuario: CriarRegistro,
) -> None:
    empresa_a, empresa_b = criar_empresa(), criar_empresa()
    administrador_de_a, membro_de_a, membro_de_b = criar_usuario(), criar_usuario(), criar_usuario()
    vincular(vinculos, administrador_de_a, empresa_a, administrador=True)
    vincular(vinculos, membro_de_a, empresa_a)
    vincular(vinculos, membro_de_b, empresa_b)

    permissoes.exigir_pode_ver_usuario(solicitante_comum(membro_de_a), membro_de_a)
    permissoes.exigir_pode_ver_usuario(solicitante_comum(administrador_de_a), membro_de_a)
    with pytest.raises(PermissaoNegada):
        permissoes.exigir_pode_ver_usuario(solicitante_comum(administrador_de_a), membro_de_b)
    with pytest.raises(PermissaoNegada):
        permissoes.exigir_pode_ver_usuario(solicitante_comum(membro_de_b), membro_de_a)
