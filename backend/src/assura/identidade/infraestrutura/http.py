from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, status
from pydantic import BaseModel

from assura.compartilhado.infraestrutura.http import (
    CategoriaDeErro,
    SessaoDoBanco,
    registrar_traducao_de_erros,
)
from assura.historico import ConsultaAOutraEmpresaNaoPermitida, ErroDoHistorico
from assura.identidade.aplicacao.autenticar import Autenticar
from assura.identidade.aplicacao.portas import EmissorDeSessao
from assura.identidade.aplicacao.trocar_propria_senha import TrocarPropriaSenha
from assura.identidade.dominio.erros import (
    AdministradorDoSistemaJaExiste,
    CnpjJaCadastrado,
    CredenciaisInvalidas,
    EmailJaCadastrado,
    EmpresaDesativadaNaoAceitaVinculo,
    EmpresaJaAtiva,
    EmpresaJaDesativada,
    EmpresaNaoEncontrada,
    ErroDeIdentidade,
    PermissaoNegada,
    SenhaProvisoriaPrecisaSerTrocada,
    SessaoInvalida,
    UltimoAdministradorNaoPodeSerRemovido,
    UsuarioNaoEncontrado,
    VinculoDesativadoNaoPodeSerAdministrador,
    VinculoJaAtivo,
    VinculoJaDesativado,
    VinculoJaEAdministrador,
    VinculoJaExiste,
    VinculoNaoEAdministrador,
    VinculoNaoEncontrado,
)
from assura.identidade.infraestrutura.dependencias_http import (
    GeradorDeResumo,
    RepositoriosDaRequisicao,
    UsuarioDaSessao,
    obter_emissor_de_sessao,
)
from assura.identidade.infraestrutura.rotas_de_empresas import roteador_de_empresas
from assura.identidade.infraestrutura.rotas_de_historico import roteador_de_historico
from assura.identidade.infraestrutura.rotas_de_usuarios import roteador_de_usuarios
from assura.identidade.infraestrutura.rotas_de_vinculos import roteador_de_vinculos
from assura.identidade.infraestrutura.usuarios_sqlalchemy import criar_usuarios

CATEGORIAS_DOS_ERROS_DE_IDENTIDADE: dict[type[Exception], CategoriaDeErro] = {
    CredenciaisInvalidas: CategoriaDeErro.NAO_AUTENTICADO,
    SessaoInvalida: CategoriaDeErro.NAO_AUTENTICADO,
    PermissaoNegada: CategoriaDeErro.SEM_PERMISSAO,
    SenhaProvisoriaPrecisaSerTrocada: CategoriaDeErro.SEM_PERMISSAO,
    EmpresaNaoEncontrada: CategoriaDeErro.NAO_ENCONTRADO,
    UsuarioNaoEncontrado: CategoriaDeErro.NAO_ENCONTRADO,
    VinculoNaoEncontrado: CategoriaDeErro.NAO_ENCONTRADO,
    AdministradorDoSistemaJaExiste: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    CnpjJaCadastrado: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    EmailJaCadastrado: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    EmpresaDesativadaNaoAceitaVinculo: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    EmpresaJaAtiva: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    EmpresaJaDesativada: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    UltimoAdministradorNaoPodeSerRemovido: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    VinculoDesativadoNaoPodeSerAdministrador: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    VinculoJaAtivo: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    VinculoJaDesativado: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    VinculoJaEAdministrador: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    VinculoJaExiste: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
    VinculoNaoEAdministrador: CategoriaDeErro.CONFLITO_COM_O_ESTADO,
}
CATEGORIAS_DOS_ERROS_DO_HISTORICO: dict[type[Exception], CategoriaDeErro] = {
    ConsultaAOutraEmpresaNaoPermitida: CategoriaDeErro.SEM_PERMISSAO,
}


class DadosDeLogin(BaseModel):
    email: str
    senha: str


class RespostaDeLogin(BaseModel):
    token: str
    tipo: str = "bearer"
    expira_em: datetime
    senha_provisoria: bool


class DadosDoUsuarioDaSessao(BaseModel):
    id: UUID
    nome: str
    email: str
    administrador_do_sistema: bool
    senha_provisoria: bool


class DadosDeTrocaDeSenha(BaseModel):
    senha_atual: str
    nova_senha: str


roteador_de_autenticacao = APIRouter(prefix="/autenticacao", tags=["autenticação"])


@roteador_de_autenticacao.post("/login")
def entrar(
    dados: DadosDeLogin,
    sessao: SessaoDoBanco,
    gerador_de_resumo: GeradorDeResumo,
    emissor_de_sessao: Annotated[EmissorDeSessao, Depends(obter_emissor_de_sessao)],
) -> RespostaDeLogin:
    resultado = Autenticar(criar_usuarios(sessao), gerador_de_resumo, emissor_de_sessao).executar(
        email=dados.email, senha=dados.senha
    )
    return RespostaDeLogin(
        token=resultado.sessao.token,
        expira_em=resultado.sessao.expira_em,
        senha_provisoria=resultado.senha_provisoria,
    )


@roteador_de_autenticacao.get("/eu")
def informar_usuario_da_sessao(usuario: UsuarioDaSessao) -> DadosDoUsuarioDaSessao:
    return DadosDoUsuarioDaSessao(
        id=usuario.id,
        nome=usuario.nome,
        email=usuario.email.valor,
        administrador_do_sistema=usuario.administrador_do_sistema,
        senha_provisoria=usuario.senha_provisoria,
    )


@roteador_de_autenticacao.post("/eu/senha", status_code=status.HTTP_204_NO_CONTENT)
def trocar_a_propria_senha(
    dados: DadosDeTrocaDeSenha,
    usuario: UsuarioDaSessao,
    repositorios: RepositoriosDaRequisicao,
    gerador_de_resumo: GeradorDeResumo,
) -> None:
    TrocarPropriaSenha(
        repositorios.usuarios, gerador_de_resumo, repositorios.registrar_acao
    ).executar(usuario_id=usuario.id, senha_atual=dados.senha_atual, nova_senha=dados.nova_senha)
    repositorios.sessao.commit()


def registrar_rotas_de_identidade(aplicacao: FastAPI) -> None:
    for roteador in (
        roteador_de_autenticacao,
        roteador_de_empresas,
        roteador_de_usuarios,
        roteador_de_vinculos,
        roteador_de_historico,
    ):
        aplicacao.include_router(roteador)
    registrar_traducao_de_erros(aplicacao, ErroDeIdentidade, CATEGORIAS_DOS_ERROS_DE_IDENTIDADE)
    registrar_traducao_de_erros(aplicacao, ErroDoHistorico, CATEGORIAS_DOS_ERROS_DO_HISTORICO)
