from collections.abc import Callable
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from assura.historico import Autor, RegistrarAcao
from assura.identidade import (
    PermissaoNegada,
    RedefinirSenha,
    SenhaInvalida,
    UsuarioAutenticado,
    UsuarioNaoEncontrado,
    Usuarios,
    Vinculo,
    Vinculos,
)
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import GeradorDeResumoDeSenha
from tests.identidade.apoio import (
    OUTRA_SENHA,
    OUTRO_EMAIL,
    SENHA,
    cadastrar_usuario,
    criar_usuario_com_senha,
    ler_historico_do_objeto,
)


@pytest.fixture
def administrador(
    usuarios: Usuarios, registrar_acao: RegistrarAcao, gerador_de_resumo: GeradorDeResumoDeSenha
) -> UsuarioAutenticado:
    return UsuarioAutenticado.de(
        criar_usuario_com_senha(
            usuarios,
            registrar_acao,
            gerador_de_resumo,
            email="admin@assura.local",
            administrador_do_sistema=True,
        )
    )


def test_administrador_do_sistema_redefine_senha_que_vira_provisoria(
    permissoes: Permissoes,
    sessao: Session,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    administrador: UsuarioAutenticado,
) -> None:
    usuario = criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)

    RedefinirSenha(usuarios, permissoes, gerador_de_resumo, registrar_acao).executar(
        solicitante=administrador, usuario_id=usuario.id, senha_provisoria=OUTRA_SENHA
    )

    gravado = usuarios.obter(usuario.id)
    assert gravado.resumo_da_senha is not None
    assert gerador_de_resumo.conferir(gravado.resumo_da_senha, OUTRA_SENHA)
    assert not gerador_de_resumo.conferir(gravado.resumo_da_senha, SENHA)
    assert gravado.senha_provisoria
    *_, registro = ler_historico_do_objeto(sessao, "usuario", usuario.id)
    assert registro.tipo_de_acao == "senha_redefinida"
    assert registro.autor == Autor.usuario(administrador.id)
    assert registro.detalhes == {}


def test_primeira_senha_de_usuario_recem_cadastrado(
    permissoes: Permissoes,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    administrador: UsuarioAutenticado,
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao, email=OUTRO_EMAIL)

    RedefinirSenha(usuarios, permissoes, gerador_de_resumo, registrar_acao).executar(
        solicitante=administrador, usuario_id=usuario.id, senha_provisoria=SENHA
    )

    assert usuarios.obter(usuario.id).senha_provisoria


def test_quem_nao_e_administrador_do_sistema_nao_redefine(
    permissoes: Permissoes,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
) -> None:
    usuario = criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)
    comum = UsuarioAutenticado(id=uuid4(), administrador_do_sistema=False, senha_provisoria=False)

    with pytest.raises(PermissaoNegada):
        RedefinirSenha(usuarios, permissoes, gerador_de_resumo, registrar_acao).executar(
            solicitante=comum, usuario_id=usuario.id, senha_provisoria=OUTRA_SENHA
        )

    assert not usuarios.obter(usuario.id).senha_provisoria


def test_usuario_inexistente_e_senha_invalida_sao_recusados(
    permissoes: Permissoes,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    administrador: UsuarioAutenticado,
) -> None:
    redefinir = RedefinirSenha(usuarios, permissoes, gerador_de_resumo, registrar_acao)

    with pytest.raises(UsuarioNaoEncontrado):
        redefinir.executar(solicitante=administrador, usuario_id=uuid4(), senha_provisoria=SENHA)
    with pytest.raises(SenhaInvalida):
        redefinir.executar(
            solicitante=administrador, usuario_id=administrador.id, senha_provisoria="curta"
        )


def vincular_direto(
    vinculos: Vinculos, usuario_id: UUID, empresa_id: UUID, *, administrador: bool = False
) -> None:
    vinculo = Vinculo.criar(usuario_id=usuario_id, empresa_id=empresa_id)
    if administrador:
        vinculo.tornar_administrador()
    vinculos.adicionar(vinculo)


@pytest.fixture
def administrador_da_empresa_a(
    vinculos: Vinculos, criar_empresa: Callable[[], UUID], criar_usuario: Callable[[], UUID]
) -> tuple[UsuarioAutenticado, UUID]:
    empresa_a, administrador_id = criar_empresa(), criar_usuario()
    vincular_direto(vinculos, administrador_id, empresa_a, administrador=True)
    como_administrador = UsuarioAutenticado(
        id=administrador_id, administrador_do_sistema=False, senha_provisoria=False
    )
    return como_administrador, empresa_a


def test_administrador_da_empresa_redefine_senha_de_quem_so_esta_na_empresa_dele(
    usuarios: Usuarios,
    vinculos: Vinculos,
    permissoes: Permissoes,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    administrador_da_empresa_a: tuple[UsuarioAutenticado, UUID],
) -> None:
    administrador, empresa_a = administrador_da_empresa_a
    alvo = criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)
    vincular_direto(vinculos, alvo.id, empresa_a)

    RedefinirSenha(usuarios, permissoes, gerador_de_resumo, registrar_acao).executar(
        solicitante=administrador, usuario_id=alvo.id, senha_provisoria=OUTRA_SENHA
    )

    assert usuarios.obter(alvo.id).senha_provisoria


def test_administrador_da_empresa_nao_redefine_senha_de_quem_esta_em_outra_empresa(
    usuarios: Usuarios,
    vinculos: Vinculos,
    permissoes: Permissoes,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    criar_empresa: Callable[[], UUID],
    administrador_da_empresa_a: tuple[UsuarioAutenticado, UUID],
) -> None:
    administrador, empresa_a = administrador_da_empresa_a
    alvo = criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)
    vincular_direto(vinculos, alvo.id, empresa_a)
    vincular_direto(vinculos, alvo.id, criar_empresa())

    with pytest.raises(PermissaoNegada):
        RedefinirSenha(usuarios, permissoes, gerador_de_resumo, registrar_acao).executar(
            solicitante=administrador, usuario_id=alvo.id, senha_provisoria=OUTRA_SENHA
        )

    assert not usuarios.obter(alvo.id).senha_provisoria


def test_administrador_da_empresa_nao_redefine_senha_de_administrador_do_sistema(
    usuarios: Usuarios,
    vinculos: Vinculos,
    permissoes: Permissoes,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    administrador_da_empresa_a: tuple[UsuarioAutenticado, UUID],
) -> None:
    administrador, empresa_a = administrador_da_empresa_a
    root = criar_usuario_com_senha(
        usuarios, registrar_acao, gerador_de_resumo, administrador_do_sistema=True
    )
    vincular_direto(vinculos, root.id, empresa_a)

    with pytest.raises(PermissaoNegada):
        RedefinirSenha(usuarios, permissoes, gerador_de_resumo, registrar_acao).executar(
            solicitante=administrador, usuario_id=root.id, senha_provisoria=OUTRA_SENHA
        )
