from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao
from assura.identidade import (
    DesativarEmpresa,
    DesativarVinculo,
    EmpresaDesativadaNaoAceitaVinculo,
    EmpresaNaoEncontrada,
    Empresas,
    SituacaoDoVinculo,
    UsuarioNaoEncontrado,
    Usuarios,
    VincularUsuario,
    Vinculo,
    VinculoJaExiste,
    Vinculos,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.dominio.vinculo import Vinculo as EntidadeVinculo
from tests.apoio import gerar_cnpj_valido
from tests.identidade.apoio import (
    SOLICITANTE,
    cadastrar_empresa,
    cadastrar_usuario,
    ler_historico_do_objeto,
)


def vincular(
    usuarios: Usuarios,
    empresas: Empresas,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
    usuario_id: UUID,
    empresa_id: UUID,
) -> Vinculo:
    return VincularUsuario(usuarios, empresas, vinculos, registrar_acao).executar(
        solicitante=SOLICITANTE,
        usuario_id=usuario_id,
        empresa_id=empresa_id,
    )


def test_vinculo_criado_ativo_e_registrado_no_historico_da_empresa(
    sessao: Session,
    usuarios: Usuarios,
    empresas: Empresas,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)
    empresa = cadastrar_empresa(empresas, registrar_acao)

    vinculo = vincular(usuarios, empresas, vinculos, registrar_acao, usuario.id, empresa.id)

    gravado = vinculos.obter(vinculo.id)
    assert gravado.usuario_id == usuario.id
    assert gravado.empresa_id == empresa.id
    assert gravado.situacao is SituacaoDoVinculo.ATIVO
    [registro] = ler_historico_do_objeto(sessao, "vinculo", vinculo.id)
    assert registro.tipo_de_acao == "usuario_vinculado"
    assert registro.empresa_id == empresa.id
    assert registro.detalhes == {"usuario_id": str(usuario.id)}


def test_usuario_pode_ter_vinculo_com_varias_empresas(
    usuarios: Usuarios, empresas: Empresas, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)
    empresa_a = cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido())
    empresa_b = cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido())

    vincular(usuarios, empresas, vinculos, registrar_acao, usuario.id, empresa_a.id)
    vincular(usuarios, empresas, vinculos, registrar_acao, usuario.id, empresa_b.id)

    assert vinculos.existe(usuario.id, empresa_a.id)
    assert vinculos.existe(usuario.id, empresa_b.id)


@pytest.mark.parametrize("desativar_antes", [False, True])
def test_segundo_vinculo_com_a_mesma_empresa_e_recusado(
    permissoes: Permissoes,
    usuarios: Usuarios,
    empresas: Empresas,
    vinculos: Vinculos,
    registrar_acao: RegistrarAcao,
    desativar_antes: bool,
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)
    empresa = cadastrar_empresa(empresas, registrar_acao)
    vinculo = vincular(usuarios, empresas, vinculos, registrar_acao, usuario.id, empresa.id)
    if desativar_antes:
        DesativarVinculo(vinculos, permissoes, registrar_acao).executar(
            solicitante=SOLICITANTE, vinculo_id=vinculo.id
        )

    with pytest.raises(VinculoJaExiste):
        vincular(usuarios, empresas, vinculos, registrar_acao, usuario.id, empresa.id)


def test_empresa_desativada_nao_aceita_vinculo(
    usuarios: Usuarios, empresas: Empresas, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)
    empresa = cadastrar_empresa(empresas, registrar_acao)
    DesativarEmpresa(empresas, registrar_acao).executar(
        solicitante=SOLICITANTE, empresa_id=empresa.id
    )

    with pytest.raises(EmpresaDesativadaNaoAceitaVinculo):
        vincular(usuarios, empresas, vinculos, registrar_acao, usuario.id, empresa.id)

    assert not vinculos.existe(usuario.id, empresa.id)


def test_usuario_inexistente_e_recusado(
    usuarios: Usuarios, empresas: Empresas, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> None:
    empresa = cadastrar_empresa(empresas, registrar_acao)

    with pytest.raises(UsuarioNaoEncontrado):
        vincular(usuarios, empresas, vinculos, registrar_acao, uuid4(), empresa.id)


def test_empresa_inexistente_e_recusada(
    usuarios: Usuarios, empresas: Empresas, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)

    with pytest.raises(EmpresaNaoEncontrada):
        vincular(usuarios, empresas, vinculos, registrar_acao, usuario.id, uuid4())


def test_restricao_do_banco_recusa_vinculo_repetido_que_passou_pela_verificacao(
    usuarios: Usuarios, empresas: Empresas, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)
    empresa = cadastrar_empresa(empresas, registrar_acao)
    vincular(usuarios, empresas, vinculos, registrar_acao, usuario.id, empresa.id)

    with pytest.raises(VinculoJaExiste):
        vinculos.adicionar(EntidadeVinculo.criar(usuario_id=usuario.id, empresa_id=empresa.id))
