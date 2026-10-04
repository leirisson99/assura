import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from assura.historico import RegistrarAcao
from assura.identidade import (
    EmailInvalido,
    EmailJaCadastrado,
    NomeDeUsuarioInvalido,
    SituacaoDoUsuario,
    Usuario,
    Usuarios,
)
from assura.identidade.dominio.email import Email
from assura.identidade.infraestrutura.tabela import tabela_usuario
from tests.identidade.apoio import (
    AUTOR,
    EMAIL,
    INSTANTE,
    cadastrar_usuario,
    ler_historico_do_objeto,
)

# A fixture `sessao` já grava o usuário autor de teste.
USUARIOS_JA_GRAVADOS = 1


def contar_usuarios(sessao: Session) -> int:
    total = sessao.scalar(select(func.count()).select_from(tabela_usuario)) or 0
    return total - USUARIOS_JA_GRAVADOS


def test_usuario_cadastrado_fica_gravado_ativo_e_com_email_em_minusculas(
    usuarios: Usuarios, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao, email=" Maria@Empresa.COM ")

    gravado = usuarios.obter(usuario.id)
    assert gravado.nome == "Maria Souza"
    assert gravado.email.valor == "maria@empresa.com"
    assert gravado.situacao is SituacaoDoUsuario.ATIVO


def test_cadastro_fica_no_historico_sem_empresa_e_sem_dados_pessoais(
    sessao: Session, usuarios: Usuarios, registrar_acao: RegistrarAcao
) -> None:
    usuario = cadastrar_usuario(usuarios, registrar_acao)

    [registro] = ler_historico_do_objeto(sessao, "usuario", usuario.id)
    assert registro.tipo_de_acao == "usuario_cadastrado"
    assert registro.autor == AUTOR
    assert registro.empresa_id is None
    assert registro.registrado_em == INSTANTE
    assert registro.detalhes == {}


def test_email_ja_cadastrado_com_outras_maiusculas_e_recusado(
    sessao: Session, usuarios: Usuarios, registrar_acao: RegistrarAcao
) -> None:
    cadastrar_usuario(usuarios, registrar_acao, email=EMAIL)

    with pytest.raises(EmailJaCadastrado):
        cadastrar_usuario(usuarios, registrar_acao, nome="Outra", email=EMAIL.upper())

    assert contar_usuarios(sessao) == 1


@pytest.mark.parametrize(
    ("dados_invalidos", "erro"),
    [({"email": "maria@empresa"}, EmailInvalido), ({"nome": "  "}, NomeDeUsuarioInvalido)],
)
def test_dados_invalidos_nao_gravam_usuario(
    sessao: Session,
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    dados_invalidos: dict[str, str],
    erro: type[Exception],
) -> None:
    with pytest.raises(erro):
        cadastrar_usuario(usuarios, registrar_acao, **dados_invalidos)

    assert contar_usuarios(sessao) == 0


def test_restricao_do_banco_recusa_email_repetido_que_passou_pela_verificacao(
    sessao: Session, usuarios: Usuarios, registrar_acao: RegistrarAcao
) -> None:
    cadastrar_usuario(usuarios, registrar_acao)
    concorrente = Usuario.cadastrar(nome="Concorrente", email=Email.criar(EMAIL))

    with pytest.raises(EmailJaCadastrado):
        usuarios.adicionar(concorrente)

    assert contar_usuarios(sessao) == 1
