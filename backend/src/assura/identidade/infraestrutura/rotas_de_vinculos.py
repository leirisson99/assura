from uuid import UUID

from fastapi import APIRouter

from assura.identidade.aplicacao.administrador_da_empresa import (
    RemoverAdministrador,
    TornarAdministrador,
)
from assura.identidade.aplicacao.mudar_situacao_do_vinculo import (
    DesativarVinculo,
    ReativarVinculo,
)
from assura.identidade.infraestrutura.dependencias_http import (
    RepositoriosDaRequisicao,
    Solicitante,
)
from assura.identidade.infraestrutura.respostas_http import VinculoResposta

roteador_de_vinculos = APIRouter(prefix="/vinculos", tags=["vínculos"])


@roteador_de_vinculos.post("/{vinculo_id}/desativacao")
def desativar_vinculo(
    vinculo_id: UUID, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> VinculoResposta:
    vinculo = DesativarVinculo(
        repositorios.vinculos, repositorios.permissoes, repositorios.registrar_acao
    ).executar(solicitante=solicitante, vinculo_id=vinculo_id)
    repositorios.sessao.commit()
    return VinculoResposta.de(vinculo)


@roteador_de_vinculos.post("/{vinculo_id}/reativacao")
def reativar_vinculo(
    vinculo_id: UUID, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> VinculoResposta:
    vinculo = ReativarVinculo(
        repositorios.vinculos, repositorios.permissoes, repositorios.registrar_acao
    ).executar(solicitante=solicitante, vinculo_id=vinculo_id)
    repositorios.sessao.commit()
    return VinculoResposta.de(vinculo)


@roteador_de_vinculos.post("/{vinculo_id}/administrador")
def tornar_administrador(
    vinculo_id: UUID, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> VinculoResposta:
    vinculo = TornarAdministrador(
        repositorios.vinculos, repositorios.permissoes, repositorios.registrar_acao
    ).executar(solicitante=solicitante, vinculo_id=vinculo_id)
    repositorios.sessao.commit()
    return VinculoResposta.de(vinculo)


@roteador_de_vinculos.delete("/{vinculo_id}/administrador")
def remover_administrador(
    vinculo_id: UUID, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> VinculoResposta:
    vinculo = RemoverAdministrador(
        repositorios.vinculos, repositorios.permissoes, repositorios.registrar_acao
    ).executar(solicitante=solicitante, vinculo_id=vinculo_id)
    repositorios.sessao.commit()
    return VinculoResposta.de(vinculo)
