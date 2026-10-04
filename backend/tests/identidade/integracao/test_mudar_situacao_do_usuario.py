from collections.abc import Callable
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao, TipoDeAcao
from assura.identidade import (
    Autenticar,
    DesativarEmpresa,
    DesativarUsuario,
    Empresas,
    PermissaoNegada,
    ReativarUsuario,
    SituacaoDoUsuario,
    SituacaoDoVinculo,
    UltimoAdministradorDoSistemaNaoPodeSerDesativado,
    UltimoAdministradorNaoPodeSerRemovido,
    Usuario,
    UsuarioAutenticado,
    UsuarioJaAtivo,
    UsuarioJaDesativado,
    Usuarios,
    VincularUsuario,
    Vinculo,
    Vinculos,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import EmissorDeSessao, GeradorDeResumoDeSenha
from tests.apoio import gerar_cnpj_valido
from tests.identidade.apoio import (
    SENHA,
    SOLICITANTE,
    SOLICITANTE_COMUM,
    cadastrar_empresa,
    criar_usuario_com_senha,
    ler_historico_do_objeto,
)

type Desativar = Callable[..., Usuario]
type Reativar = Callable[..., Usuario]


@pytest.fixture
def usuario(
    usuarios: Usuarios, registrar_acao: RegistrarAcao, gerador_de_resumo: GeradorDeResumoDeSenha
) -> Usuario:
    return criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)


@pytest.fixture
def vincular(
    usuarios: Usuarios, empresas: Empresas, vinculos: Vinculos, registrar_acao: RegistrarAcao
) -> Callable[[UUID], Vinculo]:
    def executar(usuario_id: UUID) -> Vinculo:
        empresa = cadastrar_empresa(empresas, registrar_acao, cnpj=gerar_cnpj_valido())
        return VincularUsuario(usuarios, empresas, vinculos, registrar_acao).executar(
            solicitante=SOLICITANTE, usuario_id=usuario_id, empresa_id=empresa.id
        )

    return executar


@pytest.fixture
def desativar(
    usuarios: Usuarios,
    vinculos: Vinculos,
    empresas: Empresas,
    permissoes: Permissoes,
    registrar_acao: RegistrarAcao,
) -> Desativar:
    def executar(usuario_id: UUID, solicitante: UsuarioAutenticado = SOLICITANTE) -> Usuario:
        return DesativarUsuario(usuarios, vinculos, empresas, permissoes, registrar_acao).executar(
            solicitante=solicitante, usuario_id=usuario_id
        )

    return executar


@pytest.fixture
def reativar(usuarios: Usuarios, permissoes: Permissoes, registrar_acao: RegistrarAcao) -> Reativar:
    def executar(usuario_id: UUID, solicitante: UsuarioAutenticado = SOLICITANTE) -> Usuario:
        return ReativarUsuario(usuarios, permissoes, registrar_acao).executar(
            solicitante=solicitante, usuario_id=usuario_id
        )

    return executar


def tipos_no_historico(sessao: Session, usuario_id: UUID) -> list[str]:
    return [
        registro.tipo_de_acao for registro in ler_historico_do_objeto(sessao, "usuario", usuario_id)
    ]


def test_desativar_usuario_grava_a_situacao_e_o_historico_sem_empresa(
    sessao: Session, usuarios: Usuarios, usuario: Usuario, desativar: Desativar
) -> None:
    desativar(usuario.id)

    assert usuarios.obter(usuario.id).situacao is SituacaoDoUsuario.DESATIVADO
    ultimo_registro = ler_historico_do_objeto(sessao, "usuario", usuario.id)[-1]
    assert ultimo_registro.tipo_de_acao == TipoDeAcao.USUARIO_DESATIVADO
    assert ultimo_registro.empresa_id is None


def test_desativar_usuario_mantem_dados_senha_e_vinculos(
    usuarios: Usuarios,
    vinculos: Vinculos,
    usuario: Usuario,
    vincular: Callable[[UUID], Vinculo],
    desativar: Desativar,
) -> None:
    vinculo = vincular(usuario.id)

    desativar(usuario.id)

    guardado = usuarios.obter(usuario.id)
    assert (guardado.nome, guardado.email) == (usuario.nome, usuario.email)
    assert guardado.resumo_da_senha == usuario.resumo_da_senha
    assert vinculos.obter(vinculo.id).situacao is SituacaoDoVinculo.ATIVO


def test_desativar_usuario_ja_desativado_e_recusado_sem_registro(
    sessao: Session, usuario: Usuario, desativar: Desativar
) -> None:
    desativar(usuario.id)
    tipos_antes = tipos_no_historico(sessao, usuario.id)

    with pytest.raises(UsuarioJaDesativado):
        desativar(usuario.id)

    assert tipos_no_historico(sessao, usuario.id) == tipos_antes


def test_usuario_comum_nao_desativa_usuario(usuario: Usuario, desativar: Desativar) -> None:
    with pytest.raises(PermissaoNegada):
        desativar(usuario.id, SOLICITANTE_COMUM)


def test_administrador_da_empresa_nao_desativa_usuario(
    usuario: Usuario,
    vincular: Callable[[UUID], Vinculo],
    vinculos: Vinculos,
    desativar: Desativar,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
) -> None:
    vinculo_do_alvo = vincular(usuario.id)
    administrador = criar_usuario_com_senha(
        usuarios, registrar_acao, gerador_de_resumo, email="adm@empresa.com"
    )
    vinculo_do_administrador = Vinculo.criar(
        usuario_id=administrador.id, empresa_id=vinculo_do_alvo.empresa_id
    )
    vinculo_do_administrador.tornar_administrador()
    vinculos.adicionar(vinculo_do_administrador)

    with pytest.raises(PermissaoNegada):
        desativar(
            usuario.id,
            UsuarioAutenticado(
                id=administrador.id, administrador_do_sistema=False, senha_provisoria=False
            ),
        )


def tornar_administrador(vinculos: Vinculos, vinculo: Vinculo) -> None:
    vinculo.tornar_administrador()
    vinculos.atualizar(vinculo)


def test_unico_administrador_de_uma_empresa_nao_e_desativado(
    usuario: Usuario,
    vincular: Callable[[UUID], Vinculo],
    vinculos: Vinculos,
    usuarios: Usuarios,
    desativar: Desativar,
) -> None:
    vincular(usuario.id)
    tornar_administrador(vinculos, vincular(usuario.id))

    with pytest.raises(UltimoAdministradorNaoPodeSerRemovido, match="Empresa X Ltda"):
        desativar(usuario.id)

    assert usuarios.obter(usuario.id).situacao is SituacaoDoUsuario.ATIVO


def test_unico_administrador_de_empresa_desativada_tambem_nao_e_desativado(
    usuario: Usuario,
    vincular: Callable[[UUID], Vinculo],
    vinculos: Vinculos,
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    desativar: Desativar,
) -> None:
    vinculo = vincular(usuario.id)
    tornar_administrador(vinculos, vinculo)
    DesativarEmpresa(empresas, registrar_acao).executar(
        solicitante=SOLICITANTE, empresa_id=vinculo.empresa_id
    )

    with pytest.raises(UltimoAdministradorNaoPodeSerRemovido):
        desativar(usuario.id)


def test_com_dois_administradores_um_deles_pode_ser_desativado(
    usuario: Usuario,
    vincular: Callable[[UUID], Vinculo],
    vinculos: Vinculos,
    usuarios: Usuarios,
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    desativar: Desativar,
) -> None:
    vinculo = vincular(usuario.id)
    tornar_administrador(vinculos, vinculo)
    outro = criar_usuario_com_senha(
        usuarios, registrar_acao, gerador_de_resumo, email="joao@empresa.com"
    )
    vinculo_do_outro = VincularUsuario(usuarios, empresas, vinculos, registrar_acao).executar(
        solicitante=SOLICITANTE, usuario_id=outro.id, empresa_id=vinculo.empresa_id
    )
    tornar_administrador(vinculos, vinculo_do_outro)

    desativar(usuario.id)

    assert vinculos.listar_administradores_ativos(vinculo.empresa_id) == [vinculo_do_outro.id]


def test_unico_administrador_do_sistema_nao_e_desativado(
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    desativar: Desativar,
) -> None:
    root = criar_usuario_com_senha(
        usuarios, registrar_acao, gerador_de_resumo, administrador_do_sistema=True
    )

    with pytest.raises(UltimoAdministradorDoSistemaNaoPodeSerDesativado):
        desativar(root.id)


def test_com_dois_administradores_do_sistema_um_pode_ser_desativado(
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    desativar: Desativar,
) -> None:
    root = criar_usuario_com_senha(
        usuarios, registrar_acao, gerador_de_resumo, administrador_do_sistema=True
    )
    criar_usuario_com_senha(
        usuarios,
        registrar_acao,
        gerador_de_resumo,
        email="outro-root@empresa.com",
        administrador_do_sistema=True,
    )

    assert desativar(root.id).situacao is SituacaoDoUsuario.DESATIVADO


def test_reativar_usuario_grava_a_situacao_e_o_historico(
    sessao: Session,
    usuarios: Usuarios,
    usuario: Usuario,
    desativar: Desativar,
    reativar: Reativar,
) -> None:
    desativar(usuario.id)

    reativar(usuario.id)

    assert usuarios.obter(usuario.id).situacao is SituacaoDoUsuario.ATIVO
    assert tipos_no_historico(sessao, usuario.id)[-2:] == [
        TipoDeAcao.USUARIO_DESATIVADO,
        TipoDeAcao.USUARIO_REATIVADO,
    ]


def test_usuario_reativado_entra_com_a_mesma_senha(
    usuarios: Usuarios,
    usuario: Usuario,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    emissor_de_sessao: EmissorDeSessao,
    desativar: Desativar,
    reativar: Reativar,
) -> None:
    desativar(usuario.id)

    reativar(usuario.id)

    resultado = Autenticar(usuarios, gerador_de_resumo, emissor_de_sessao).executar(
        email=usuario.email.valor, senha=SENHA
    )
    assert emissor_de_sessao.ler(resultado.sessao.token) == usuario.id


def test_usuario_reativado_volta_a_contar_como_administrador(
    usuario: Usuario,
    vincular: Callable[[UUID], Vinculo],
    vinculos: Vinculos,
    usuarios: Usuarios,
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    desativar: Desativar,
    reativar: Reativar,
) -> None:
    vinculo = vincular(usuario.id)
    tornar_administrador(vinculos, vinculo)
    outro = criar_usuario_com_senha(
        usuarios, registrar_acao, gerador_de_resumo, email="joao@empresa.com"
    )
    vinculo_do_outro = VincularUsuario(usuarios, empresas, vinculos, registrar_acao).executar(
        solicitante=SOLICITANTE, usuario_id=outro.id, empresa_id=vinculo.empresa_id
    )
    tornar_administrador(vinculos, vinculo_do_outro)
    desativar(usuario.id)

    reativar(usuario.id)

    assert vinculos.listar_administradores_ativos(vinculo.empresa_id) == sorted(
        [vinculo.id, vinculo_do_outro.id]
    )


def test_reativar_usuario_ja_ativo_e_recusado_sem_registro(
    sessao: Session, usuario: Usuario, reativar: Reativar
) -> None:
    tipos_antes = tipos_no_historico(sessao, usuario.id)

    with pytest.raises(UsuarioJaAtivo):
        reativar(usuario.id)

    assert tipos_no_historico(sessao, usuario.id) == tipos_antes


def test_usuario_comum_nao_reativa_usuario(
    usuario: Usuario, desativar: Desativar, reativar: Reativar
) -> None:
    desativar(usuario.id)

    with pytest.raises(PermissaoNegada):
        reativar(usuario.id, SOLICITANTE_COMUM)
