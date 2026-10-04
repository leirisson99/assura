from collections.abc import Callable
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from assura.historico import Autor, RegistrarAcao
from assura.identidade import (
    DesativarVinculo,
    Empresas,
    PermissaoNegada,
    RemoverAdministrador,
    TornarAdministrador,
    UltimoAdministradorNaoPodeSerRemovido,
    UsuarioAutenticado,
    Usuarios,
    VincularUsuario,
    Vinculo,
    VinculoDesativadoNaoPodeSerAdministrador,
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

type VincularPessoa = Callable[[UUID, str], Vinculo]


def como(vinculo: Vinculo) -> UsuarioAutenticado:
    """Solicitante que é o usuário do vínculo, sem ser administrador do sistema."""
    return UsuarioAutenticado(
        id=vinculo.usuario_id, administrador_do_sistema=False, senha_provisoria=False
    )


@pytest.fixture
def empresa_id(empresas: Empresas, registrar_acao: RegistrarAcao) -> UUID:
    return cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido()).id


@pytest.fixture
def vincular_pessoa(
    usuarios: Usuarios, empresas: Empresas, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> VincularPessoa:
    def vincular(empresa_id: UUID, email: str) -> Vinculo:
        usuario = cadastrar_usuario(usuarios, registrar_acao, nome=email, email=email)
        return VincularUsuario(usuarios, empresas, vinculos, registrar_acao).executar(
            solicitante=SOLICITANTE, usuario_id=usuario.id, empresa_id=empresa_id
        )

    return vincular


@pytest.fixture
def tornar(
    vinculos: Vinculos, permissoes: Permissoes, registrar_acao: RegistrarAcao
) -> Callable[..., Vinculo]:
    def executar(vinculo: Vinculo, solicitante: UsuarioAutenticado = SOLICITANTE) -> Vinculo:
        return TornarAdministrador(vinculos, permissoes, registrar_acao).executar(
            solicitante=solicitante, vinculo_id=vinculo.id
        )

    return executar


@pytest.fixture
def remover(
    vinculos: Vinculos, permissoes: Permissoes, registrar_acao: RegistrarAcao
) -> Callable[..., Vinculo]:
    def executar(vinculo: Vinculo, solicitante: UsuarioAutenticado = SOLICITANTE) -> Vinculo:
        return RemoverAdministrador(vinculos, permissoes, registrar_acao).executar(
            solicitante=solicitante, vinculo_id=vinculo.id
        )

    return executar


def test_tornar_administrador_grava_o_papel_e_o_historico(
    sessao: Session,
    vinculos: Vinculos,
    empresa_id: UUID,
    vincular_pessoa: VincularPessoa,
    tornar: Callable[..., Vinculo],
) -> None:
    vinculo = vincular_pessoa(empresa_id, "maria@empresa.com")

    tornar(vinculo)

    assert vinculos.obter(vinculo.id).administrador_da_empresa
    *_, registro = ler_historico_do_objeto(sessao, "vinculo", vinculo.id)
    assert registro.tipo_de_acao == "administrador_definido"
    assert registro.empresa_id == empresa_id
    assert registro.autor == Autor.usuario(SOLICITANTE.id)
    assert registro.detalhes == {"usuario_id": str(vinculo.usuario_id)}


def test_com_dois_administradores_um_pode_deixar_de_ser(
    sessao: Session,
    vinculos: Vinculos,
    empresa_id: UUID,
    vincular_pessoa: VincularPessoa,
    tornar: Callable[..., Vinculo],
    remover: Callable[..., Vinculo],
) -> None:
    maria = tornar(vincular_pessoa(empresa_id, "maria@empresa.com"))
    joao = tornar(vincular_pessoa(empresa_id, "joao@empresa.com"))

    remover(joao, como(maria))

    assert not vinculos.obter(joao.id).administrador_da_empresa
    *_, registro = ler_historico_do_objeto(sessao, "vinculo", joao.id)
    assert registro.tipo_de_acao == "administrador_removido"
    assert registro.autor == Autor.usuario(maria.usuario_id)


def test_ultimo_administrador_nao_perde_o_papel(
    vinculos: Vinculos,
    empresa_id: UUID,
    vincular_pessoa: VincularPessoa,
    tornar: Callable[..., Vinculo],
    remover: Callable[..., Vinculo],
) -> None:
    maria = tornar(vincular_pessoa(empresa_id, "maria@empresa.com"))

    with pytest.raises(UltimoAdministradorNaoPodeSerRemovido):
        remover(maria)

    assert vinculos.obter(maria.id).administrador_da_empresa


def test_vinculo_do_ultimo_administrador_nao_e_desativado(
    vinculos: Vinculos,
    permissoes: Permissoes,
    registrar_acao: RegistrarAcao,
    empresa_id: UUID,
    vincular_pessoa: VincularPessoa,
    tornar: Callable[..., Vinculo],
) -> None:
    maria = tornar(vincular_pessoa(empresa_id, "maria@empresa.com"))

    with pytest.raises(UltimoAdministradorNaoPodeSerRemovido):
        DesativarVinculo(vinculos, permissoes, registrar_acao).executar(
            solicitante=como(maria), vinculo_id=maria.id
        )


def test_vinculo_desativado_nao_vira_administrador(
    vinculos: Vinculos,
    permissoes: Permissoes,
    registrar_acao: RegistrarAcao,
    empresa_id: UUID,
    vincular_pessoa: VincularPessoa,
    tornar: Callable[..., Vinculo],
) -> None:
    vinculo = vincular_pessoa(empresa_id, "maria@empresa.com")
    DesativarVinculo(vinculos, permissoes, registrar_acao).executar(
        solicitante=SOLICITANTE, vinculo_id=vinculo.id
    )

    with pytest.raises(VinculoDesativadoNaoPodeSerAdministrador):
        tornar(vinculo)


def test_administrador_da_empresa_torna_outro_administrador(
    vinculos: Vinculos,
    empresa_id: UUID,
    vincular_pessoa: VincularPessoa,
    tornar: Callable[..., Vinculo],
) -> None:
    maria = tornar(vincular_pessoa(empresa_id, "maria@empresa.com"))
    joao = vincular_pessoa(empresa_id, "joao@empresa.com")

    tornar(joao, como(maria))

    assert vinculos.obter(joao.id).administrador_da_empresa


def test_membro_comum_nem_administrador_de_outra_empresa_tornam_administrador(
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    empresa_id: UUID,
    vincular_pessoa: VincularPessoa,
    tornar: Callable[..., Vinculo],
) -> None:
    outra_empresa_id = cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido()).id
    administrador_de_outra = tornar(vincular_pessoa(outra_empresa_id, "ana@outra.com"))
    membro = vincular_pessoa(empresa_id, "maria@empresa.com")
    alvo = vincular_pessoa(empresa_id, "joao@empresa.com")

    for solicitante in (como(membro), como(administrador_de_outra)):
        with pytest.raises(PermissaoNegada):
            tornar(alvo, solicitante)
