"""Cada caso de uso exclusivo do administrador do sistema recusa os demais usuários."""

from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

import pytest

from assura.historico import RegistrarAcao
from assura.identidade import (
    AlterarEmpresa,
    AlterarUsuario,
    CadastrarEmpresa,
    CadastrarUsuario,
    ConsultarEmpresas,
    DesativarEmpresa,
    Empresas,
    PermissaoNegada,
    ReativarEmpresa,
    Usuarios,
    VincularUsuario,
    Vinculos,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from tests.identidade.apoio import CNPJ_NUMERICO, EMAIL, SOLICITANTE_COMUM


@dataclass(frozen=True)
class Repositorios:
    usuarios: Usuarios
    empresas: Empresas
    vinculos: Vinculos
    permissoes: Permissoes
    registrar_acao: RegistrarAcao


type Acao = Callable[[Repositorios], object]

ACOES_DO_ADMINISTRADOR_DO_SISTEMA: dict[str, Acao] = {
    "cadastrar empresa": lambda repositorios: CadastrarEmpresa(
        repositorios.empresas, repositorios.registrar_acao
    ).executar(
        solicitante=SOLICITANTE_COMUM, razao_social="X", nome_fantasia=None, cnpj=CNPJ_NUMERICO
    ),
    "alterar empresa": lambda repositorios: AlterarEmpresa(
        repositorios.empresas, repositorios.registrar_acao
    ).executar(
        solicitante=SOLICITANTE_COMUM,
        empresa_id=uuid4(),
        razao_social="X",
        nome_fantasia=None,
        cnpj=CNPJ_NUMERICO,
    ),
    "desativar empresa": lambda repositorios: DesativarEmpresa(
        repositorios.empresas, repositorios.registrar_acao
    ).executar(solicitante=SOLICITANTE_COMUM, empresa_id=uuid4()),
    "reativar empresa": lambda repositorios: ReativarEmpresa(
        repositorios.empresas, repositorios.registrar_acao
    ).executar(solicitante=SOLICITANTE_COMUM, empresa_id=uuid4()),
    "listar empresas": lambda repositorios: ConsultarEmpresas(
        repositorios.empresas, repositorios.permissoes
    ).listar(solicitante=SOLICITANTE_COMUM),
    "cadastrar usuário": lambda repositorios: CadastrarUsuario(
        repositorios.usuarios, repositorios.registrar_acao
    ).executar(solicitante=SOLICITANTE_COMUM, nome="Maria", email=EMAIL),
    "alterar usuário": lambda repositorios: AlterarUsuario(
        repositorios.usuarios, repositorios.registrar_acao
    ).executar(solicitante=SOLICITANTE_COMUM, usuario_id=uuid4(), nome="Maria", email=EMAIL),
    "vincular usuário por id": lambda repositorios: VincularUsuario(
        repositorios.usuarios,
        repositorios.empresas,
        repositorios.vinculos,
        repositorios.registrar_acao,
    ).executar(solicitante=SOLICITANTE_COMUM, usuario_id=uuid4(), empresa_id=uuid4()),
}


@pytest.mark.parametrize(
    "acao",
    ACOES_DO_ADMINISTRADOR_DO_SISTEMA.values(),
    ids=list(ACOES_DO_ADMINISTRADOR_DO_SISTEMA),
)
def test_acao_exclusiva_do_administrador_do_sistema_recusa_os_demais(
    usuarios: Usuarios,
    empresas: Empresas,
    vinculos: Vinculos,
    permissoes: Permissoes,
    registrar_acao: RegistrarAcao,
    acao: Acao,
) -> None:
    repositorios = Repositorios(usuarios, empresas, vinculos, permissoes, registrar_acao)

    with pytest.raises(PermissaoNegada):
        acao(repositorios)
