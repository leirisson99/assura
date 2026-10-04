from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from assura.historico import (
    ConsultarHistorico,
    FiltroDoHistorico,
    ObjetoAfetado,
    Pagina,
    RegistrarAcao,
    RegistroDeHistorico,
    SolicitanteDaConsulta,
    criar_historico,
)
from assura.identidade import (
    CadastrarEmpresa,
    CadastrarUsuario,
    Empresa,
    Empresas,
    Usuario,
    Usuarios,
)
from assura.identidade.aplicacao.portas import GeradorDeResumoDeSenha, UsuarioAutenticado
from tests.apoio import AUTOR_DE_TESTE, ID_DO_AUTOR_DE_TESTE

INSTANTE = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)
AUTOR = AUTOR_DE_TESTE
# Os casos de uso confiam no solicitante montado pela camada HTTP; nos testes, o autor de teste age
# como administrador do sistema.
SOLICITANTE = UsuarioAutenticado(
    id=ID_DO_AUTOR_DE_TESTE, administrador_do_sistema=True, senha_provisoria=False
)
SOLICITANTE_COMUM = UsuarioAutenticado(
    id=ID_DO_AUTOR_DE_TESTE, administrador_do_sistema=False, senha_provisoria=False
)
CNPJ_NUMERICO = "12.345.678/0001-95"
OUTRO_CNPJ_NUMERICO = "11.222.333/0001-81"
CNPJ_ALFANUMERICO = "12.ABC.345/01DE-35"
SENHA = "senha-correta-123"
OUTRA_SENHA = "outra-senha-456"
CHAVE_DE_SESSAO_DE_TESTE = "chave-de-sessao-dos-testes-com-32-bytes-ou-mais"


def cadastrar_empresa(
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    *,
    razao_social: str = "Empresa X Ltda",
    nome_fantasia: str | None = "Empresa X",
    cnpj: str = CNPJ_NUMERICO,
) -> Empresa:
    return CadastrarEmpresa(empresas, registrar_acao).executar(
        solicitante=SOLICITANTE, razao_social=razao_social, nome_fantasia=nome_fantasia, cnpj=cnpj
    )


def ler_historico_da_empresa(sessao: Session, empresa_id: UUID) -> list[RegistroDeHistorico]:
    """Registros da empresa, do mais antigo para o mais recente."""
    registros = ConsultarHistorico(criar_historico(sessao)).executar(
        solicitante=SolicitanteDaConsulta.administrador_do_sistema(),
        filtro=FiltroDoHistorico(objeto=ObjetoAfetado("empresa", str(empresa_id))),
        pagina=Pagina(),
    )
    return list(reversed(registros))


EMAIL = "maria@empresa.com"
OUTRO_EMAIL = "joao@empresa.com"


def cadastrar_usuario(
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    *,
    nome: str = "Maria Souza",
    email: str = EMAIL,
) -> Usuario:
    return CadastrarUsuario(usuarios, registrar_acao).executar(
        solicitante=SOLICITANTE, nome=nome, email=email
    )


def ler_historico_do_objeto(
    sessao: Session, tipo_do_objeto: str, identificador: UUID
) -> list[RegistroDeHistorico]:
    """Registros do objeto, do mais antigo para o mais recente."""
    registros = ConsultarHistorico(criar_historico(sessao)).executar(
        solicitante=SolicitanteDaConsulta.administrador_do_sistema(),
        filtro=FiltroDoHistorico(objeto=ObjetoAfetado(tipo_do_objeto, str(identificador))),
        pagina=Pagina(),
    )
    return list(reversed(registros))


def criar_usuario_com_senha(
    usuarios: Usuarios,
    registrar_acao: RegistrarAcao,
    gerador_de_resumo: GeradorDeResumoDeSenha,
    *,
    email: str = EMAIL,
    senha: str = SENHA,
    senha_provisoria: bool = False,
    administrador_do_sistema: bool = False,
) -> Usuario:
    """Grava um usuário com senha sem passar pelos casos de uso de senha."""
    usuario = cadastrar_usuario(usuarios, registrar_acao, email=email)
    resumo = gerador_de_resumo.gerar(senha)
    if senha_provisoria:
        usuario.definir_senha_provisoria(resumo)
    else:
        usuario.definir_senha_definitiva(resumo)
    usuario.administrador_do_sistema = administrador_do_sistema
    usuarios.atualizar(usuario)
    return usuario
