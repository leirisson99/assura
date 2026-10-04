from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao
from assura.identidade import (
    AlterarUsuario,
    EmailJaCadastrado,
    UsuarioNaoEncontrado,
    Usuarios,
)
from tests.identidade.apoio import (
    EMAIL,
    OUTRO_EMAIL,
    SOLICITANTE,
    cadastrar_usuario,
    ler_historico_do_objeto,
)


def test_alteracao_fica_gravada_e_historico_tem_so_o_que_mudou(
    sessao: Session, usuarios: Usuarios, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)

    AlterarUsuario(usuarios, registrar_acao).executar(
        solicitante=SOLICITANTE, usuario_id=usuario.id, nome="Maria S. Souza", email=EMAIL
    )

    assert usuarios.obter(usuario.id).nome == "Maria S. Souza"
    _, alteracao = ler_historico_do_objeto(sessao, "usuario", usuario.id)
    assert alteracao.tipo_de_acao == "usuario_alterado"
    assert alteracao.empresa_id is None
    assert alteracao.detalhes == {"nome": {"anterior": "Maria Souza", "novo": "Maria S. Souza"}}


def test_email_de_outro_usuario_e_recusado_e_usuario_continua_igual(
    sessao: Session, usuarios: Usuarios, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)
    cadastrar_usuario(usuarios, registrar_acao, nome="João", email=OUTRO_EMAIL)

    with pytest.raises(EmailJaCadastrado):
        AlterarUsuario(usuarios, registrar_acao).executar(
            solicitante=SOLICITANTE, usuario_id=usuario.id, nome="Nova", email=OUTRO_EMAIL.upper()
        )

    assert usuarios.obter(usuario.id).email.valor == EMAIL
    assert len(ler_historico_do_objeto(sessao, "usuario", usuario.id)) == 1


def test_alteracao_sem_mudanca_nao_gera_registro(
    sessao: Session, usuarios: Usuarios, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)

    AlterarUsuario(usuarios, registrar_acao).executar(
        solicitante=SOLICITANTE, usuario_id=usuario.id, nome=" Maria Souza ", email=EMAIL.upper()
    )

    assert len(ler_historico_do_objeto(sessao, "usuario", usuario.id)) == 1


def test_usuario_inexistente_e_recusado(usuarios: Usuarios, registrar_acao: RegistrarAcao) -> None:
    with pytest.raises(UsuarioNaoEncontrado):
        AlterarUsuario(usuarios, registrar_acao).executar(
            solicitante=SOLICITANTE, usuario_id=uuid4(), nome="Maria", email=EMAIL
        )
