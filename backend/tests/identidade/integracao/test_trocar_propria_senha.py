import pytest
from sqlalchemy.orm import Session

from assura.historico import Autor, RegistrarAcao
from assura.identidade import (
    SenhaAtualIncorreta,
    SenhaInvalida,
    TrocarPropriaSenha,
    Usuario,
    Usuarios,
)
from assura.identidade.aplicacao.portas import GeradorDeResumoDeSenha
from tests.identidade.apoio import (
    OUTRA_SENHA,
    SENHA,
    criar_usuario_com_senha,
    ler_historico_do_objeto,
)


def trocar(
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    registrar_acao: RegistrarAcao,
    usuario: Usuario,
    senha_atual: str,
    nova_senha: str,
) -> None:
    TrocarPropriaSenha(usuarios, gerador_de_resumo, registrar_acao).executar(
        usuario_id=usuario.id, senha_atual=senha_atual, nova_senha=nova_senha
    )


def test_troca_faz_a_nova_senha_valer_e_deixa_de_ser_provisoria(
    sessao: Session,
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    registrar_acao: RegistrarAcao,
) -> None:
    usuario = criar_usuario_com_senha(
        usuarios, registrar_acao, gerador_de_resumo, senha_provisoria=True
    )

    trocar(usuarios, gerador_de_resumo, registrar_acao, usuario, SENHA, OUTRA_SENHA)

    gravado = usuarios.obter(usuario.id)
    assert gravado.resumo_da_senha is not None
    assert gerador_de_resumo.conferir(gravado.resumo_da_senha, OUTRA_SENHA)
    assert not gerador_de_resumo.conferir(gravado.resumo_da_senha, SENHA)
    assert not gravado.senha_provisoria
    *_, registro = ler_historico_do_objeto(sessao, "usuario", usuario.id)
    assert registro.tipo_de_acao == "senha_trocada"
    assert registro.autor == Autor.usuario(usuario.id)
    assert registro.empresa_id is None
    assert registro.detalhes == {}


def test_senha_atual_errada_e_recusada(
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    registrar_acao: RegistrarAcao,
) -> None:
    usuario = criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)

    with pytest.raises(SenhaAtualIncorreta):
        trocar(usuarios, gerador_de_resumo, registrar_acao, usuario, "errada-123", OUTRA_SENHA)


def test_nova_senha_invalida_e_recusada_e_a_atual_continua_valendo(
    usuarios: Usuarios,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    registrar_acao: RegistrarAcao,
) -> None:
    usuario = criar_usuario_com_senha(usuarios, registrar_acao, gerador_de_resumo)

    with pytest.raises(SenhaInvalida):
        trocar(usuarios, gerador_de_resumo, registrar_acao, usuario, SENHA, "curta")

    resumo = usuarios.obter(usuario.id).resumo_da_senha
    assert resumo is not None
    assert gerador_de_resumo.conferir(resumo, SENHA)
