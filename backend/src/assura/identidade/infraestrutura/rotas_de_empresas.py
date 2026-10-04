from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from assura.identidade.aplicacao.alterar_empresa import AlterarEmpresa
from assura.identidade.aplicacao.cadastrar_empresa import CadastrarEmpresa
from assura.identidade.aplicacao.consultar_empresas import ConsultarEmpresas
from assura.identidade.aplicacao.consultar_usuarios import ConsultarUsuarios
from assura.identidade.aplicacao.incluir_usuario_na_empresa import IncluirUsuarioNaEmpresa
from assura.identidade.aplicacao.mudar_situacao_da_empresa import (
    DesativarEmpresa,
    ReativarEmpresa,
)
from assura.identidade.dominio.empresa import SituacaoDaEmpresa
from assura.identidade.dominio.vinculo import SituacaoDoVinculo
from assura.identidade.infraestrutura.dependencias_http import (
    PaginaPedida,
    RepositoriosDaRequisicao,
    Solicitante,
)
from assura.identidade.infraestrutura.respostas_http import (
    EmpresaResposta,
    UsuarioDaEmpresaResposta,
)

roteador_de_empresas = APIRouter(prefix="/empresas", tags=["empresas"])


class DadosDaEmpresa(BaseModel):
    razao_social: str
    nome_fantasia: str | None = None
    cnpj: str


class DadosDaPessoa(BaseModel):
    nome: str
    email: str


@roteador_de_empresas.post("", status_code=status.HTTP_201_CREATED)
def cadastrar_empresa(
    dados: DadosDaEmpresa, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> EmpresaResposta:
    empresa = CadastrarEmpresa(repositorios.empresas, repositorios.registrar_acao).executar(
        solicitante=solicitante,
        razao_social=dados.razao_social,
        nome_fantasia=dados.nome_fantasia,
        cnpj=dados.cnpj,
    )
    repositorios.sessao.commit()
    return EmpresaResposta.de(empresa)


@roteador_de_empresas.get("")
def listar_empresas(
    solicitante: Solicitante,
    repositorios: RepositoriosDaRequisicao,
    pagina: PaginaPedida,
    situacao: SituacaoDaEmpresa | None = None,
) -> list[EmpresaResposta]:
    empresas = ConsultarEmpresas(repositorios.empresas, repositorios.permissoes).listar(
        solicitante=solicitante, situacao=situacao, pagina=pagina
    )
    return [EmpresaResposta.de(empresa) for empresa in empresas]


@roteador_de_empresas.get("/{empresa_id}")
def obter_empresa(
    empresa_id: UUID, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> EmpresaResposta:
    empresa = ConsultarEmpresas(repositorios.empresas, repositorios.permissoes).obter(
        solicitante=solicitante, empresa_id=empresa_id
    )
    return EmpresaResposta.de(empresa)


@roteador_de_empresas.put("/{empresa_id}")
def alterar_empresa(
    empresa_id: UUID,
    dados: DadosDaEmpresa,
    solicitante: Solicitante,
    repositorios: RepositoriosDaRequisicao,
) -> EmpresaResposta:
    empresa = AlterarEmpresa(repositorios.empresas, repositorios.registrar_acao).executar(
        solicitante=solicitante,
        empresa_id=empresa_id,
        razao_social=dados.razao_social,
        nome_fantasia=dados.nome_fantasia,
        cnpj=dados.cnpj,
    )
    repositorios.sessao.commit()
    return EmpresaResposta.de(empresa)


@roteador_de_empresas.post("/{empresa_id}/desativacao")
def desativar_empresa(
    empresa_id: UUID, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> EmpresaResposta:
    empresa = DesativarEmpresa(repositorios.empresas, repositorios.registrar_acao).executar(
        solicitante=solicitante, empresa_id=empresa_id
    )
    repositorios.sessao.commit()
    return EmpresaResposta.de(empresa)


@roteador_de_empresas.post("/{empresa_id}/reativacao")
def reativar_empresa(
    empresa_id: UUID, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> EmpresaResposta:
    empresa = ReativarEmpresa(repositorios.empresas, repositorios.registrar_acao).executar(
        solicitante=solicitante, empresa_id=empresa_id
    )
    repositorios.sessao.commit()
    return EmpresaResposta.de(empresa)


@roteador_de_empresas.get("/{empresa_id}/usuarios")
def listar_usuarios_da_empresa(
    empresa_id: UUID,
    solicitante: Solicitante,
    repositorios: RepositoriosDaRequisicao,
    pagina: PaginaPedida,
    situacao: SituacaoDoVinculo | None = None,
) -> list[UsuarioDaEmpresaResposta]:
    usuarios_da_empresa = ConsultarUsuarios(
        repositorios.usuarios, repositorios.vinculos, repositorios.permissoes
    ).listar_da_empresa(
        solicitante=solicitante, empresa_id=empresa_id, situacao=situacao, pagina=pagina
    )
    return [UsuarioDaEmpresaResposta.de(item) for item in usuarios_da_empresa]


@roteador_de_empresas.post("/{empresa_id}/usuarios", status_code=status.HTTP_201_CREATED)
def incluir_usuario_na_empresa(
    empresa_id: UUID,
    dados: DadosDaPessoa,
    solicitante: Solicitante,
    repositorios: RepositoriosDaRequisicao,
) -> UsuarioDaEmpresaResposta:
    incluido = IncluirUsuarioNaEmpresa(
        repositorios.usuarios,
        repositorios.empresas,
        repositorios.vinculos,
        repositorios.permissoes,
        repositorios.registrar_acao,
    ).executar(solicitante=solicitante, empresa_id=empresa_id, nome=dados.nome, email=dados.email)
    repositorios.sessao.commit()
    return UsuarioDaEmpresaResposta.de(incluido)
