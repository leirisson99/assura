from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from assura.historico import (
    Autor,
    ConsultarHistorico,
    FiltroDoHistorico,
    ObjetoAfetado,
    Pagina,
    RegistrarAcao,
    RegistroDeHistorico,
    SolicitanteDaConsulta,
    criar_historico,
)
from assura.identidade import CadastrarEmpresa, Empresa, Empresas

INSTANTE = datetime(2026, 10, 4, 12, 0, tzinfo=UTC)
AUTOR = Autor.usuario(uuid4())
CNPJ_NUMERICO = "12.345.678/0001-95"
OUTRO_CNPJ_NUMERICO = "11.222.333/0001-81"
CNPJ_ALFANUMERICO = "12.ABC.345/01DE-35"


def cadastrar_empresa(
    empresas: Empresas,
    registrar_acao: RegistrarAcao,
    *,
    razao_social: str = "Empresa X Ltda",
    nome_fantasia: str | None = "Empresa X",
    cnpj: str = CNPJ_NUMERICO,
) -> Empresa:
    return CadastrarEmpresa(empresas, registrar_acao).executar(
        autor=AUTOR, razao_social=razao_social, nome_fantasia=nome_fantasia, cnpj=cnpj
    )


def ler_historico_da_empresa(sessao: Session, empresa_id: UUID) -> list[RegistroDeHistorico]:
    """Registros da empresa, do mais antigo para o mais recente."""
    registros = ConsultarHistorico(criar_historico(sessao)).executar(
        solicitante=SolicitanteDaConsulta.administrador_do_sistema(),
        filtro=FiltroDoHistorico(objeto=ObjetoAfetado("empresa", str(empresa_id))),
        pagina=Pagina(),
    )
    return list(reversed(registros))
