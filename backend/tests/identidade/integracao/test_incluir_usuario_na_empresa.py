from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao
from assura.identidade import (
    Empresas,
    IncluirUsuarioNaEmpresa,
    PermissaoNegada,
    SituacaoDoVinculo,
    UsuarioAutenticado,
    UsuarioDaEmpresa,
    Usuarios,
    VinculoJaExiste,
    Vinculos,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.dominio.email import Email
from tests.apoio import gerar_cnpj_valido
from tests.identidade.apoio import (
    SOLICITANTE,
    cadastrar_empresa,
    cadastrar_usuario,
    ler_historico_do_objeto,
)


@pytest.fixture
def empresa_id(empresas: Empresas, registrar_acao: RegistrarAcao) -> UUID:
    return cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido()).id


@pytest.fixture
def incluir(
    usuarios: Usuarios,
    empresas: Empresas,
    vinculos: Vinculos,
    permissoes: Permissoes,
    registrar_acao: RegistrarAcao,
) -> IncluirUsuarioNaEmpresa:
    return IncluirUsuarioNaEmpresa(usuarios, empresas, vinculos, permissoes, registrar_acao)


def test_email_novo_cadastra_e_vincula(
    sessao: Session, incluir: IncluirUsuarioNaEmpresa, empresa_id: UUID
) -> None:
    incluido = incluir.executar(
        solicitante=SOLICITANTE, empresa_id=empresa_id, nome="Maria", email="Maria@Empresa.com"
    )

    assert incluido.usuario.email == Email.criar("maria@empresa.com")
    assert incluido.vinculo.empresa_id == empresa_id
    assert incluido.vinculo.situacao is SituacaoDoVinculo.ATIVO
    tipos_do_usuario = [
        registro.tipo_de_acao
        for registro in ler_historico_do_objeto(sessao, "usuario", incluido.usuario.id)
    ]
    tipos_do_vinculo = [
        registro.tipo_de_acao
        for registro in ler_historico_do_objeto(sessao, "vinculo", incluido.vinculo.id)
    ]
    assert tipos_do_usuario == ["usuario_cadastrado"]
    assert tipos_do_vinculo == ["usuario_vinculado"]


def test_email_existente_vincula_o_usuario_sem_mudar_o_nome(
    sessao: Session,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    incluir: IncluirUsuarioNaEmpresa,
    empresa_id: UUID,
) -> None:
    existente = cadastrar_usuario(usuarios, registrar_acao, nome="Maria Souza")

    incluido = incluir.executar(
        solicitante=SOLICITANTE,
        empresa_id=empresa_id,
        nome="Outro Nome",
        email=existente.email.valor,
    )

    assert incluido.usuario.id == existente.id
    assert usuarios.obter(existente.id).nome == "Maria Souza"
    assert len(ler_historico_do_objeto(sessao, "usuario", existente.id)) == 1


def test_quem_ja_esta_na_empresa_nao_e_incluido_de_novo(
    incluir: IncluirUsuarioNaEmpresa, empresa_id: UUID
) -> None:
    incluir.executar(solicitante=SOLICITANTE, empresa_id=empresa_id, nome="Maria", email="m@x.com")

    with pytest.raises(VinculoJaExiste):
        incluir.executar(
            solicitante=SOLICITANTE, empresa_id=empresa_id, nome="Maria", email="m@x.com"
        )


def test_administrador_da_empresa_inclui_so_na_propria(
    vinculos: Vinculos,
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    incluir: IncluirUsuarioNaEmpresa,
    empresa_id: UUID,
) -> None:
    administrador: UsuarioDaEmpresa = incluir.executar(
        solicitante=SOLICITANTE, empresa_id=empresa_id, nome="Ana", email="ana@x.com"
    )
    administrador.vinculo.tornar_administrador()
    vinculos.atualizar(administrador.vinculo)
    como_ana = UsuarioAutenticado(
        id=administrador.usuario.id, administrador_do_sistema=False, senha_provisoria=False
    )
    outra_empresa_id = cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido()).id

    incluir.executar(solicitante=como_ana, empresa_id=empresa_id, nome="João", email="joao@x.com")
    with pytest.raises(PermissaoNegada):
        incluir.executar(
            solicitante=como_ana, empresa_id=outra_empresa_id, nome="Bia", email="bia@x.com"
        )
