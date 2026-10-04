from datetime import datetime, timedelta
from functools import cache
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from assura.compartilhado.infraestrutura.http import SessaoDoBanco
from assura.configuracao import configuracao
from assura.historico import RegistrarAcao, criar_historico
from assura.identidade.aplicacao.autenticar import Autenticar
from assura.identidade.aplicacao.portas import (
    EmissorDeSessao,
    GeradorDeResumoDeSenha,
    UsuarioAutenticado,
)
from assura.identidade.aplicacao.redefinir_senha import RedefinirSenha
from assura.identidade.aplicacao.trocar_propria_senha import TrocarPropriaSenha
from assura.identidade.dominio.erros import (
    CredenciaisInvalidas,
    ErroDeIdentidade,
    PermissaoNegada,
    SenhaAtualIncorreta,
    SenhaInvalida,
    SessaoInvalida,
    UsuarioNaoEncontrado,
)
from assura.identidade.dominio.usuario import SituacaoDoUsuario, Usuario
from assura.identidade.infraestrutura.resumo_de_senha_argon2 import GeradorDeResumoArgon2
from assura.identidade.infraestrutura.sessao_jwt import EmissorDeSessaoJwt
from assura.identidade.infraestrutura.usuarios_sqlalchemy import criar_usuarios

STATUS_POR_ERRO: dict[type[Exception], int] = {
    CredenciaisInvalidas: status.HTTP_401_UNAUTHORIZED,
    PermissaoNegada: status.HTTP_403_FORBIDDEN,
    UsuarioNaoEncontrado: status.HTTP_404_NOT_FOUND,
    SenhaInvalida: status.HTTP_422_UNPROCESSABLE_CONTENT,
    SenhaAtualIncorreta: status.HTTP_422_UNPROCESSABLE_CONTENT,
}

esquema_bearer = HTTPBearer(auto_error=False)


@cache
def obter_gerador_de_resumo() -> GeradorDeResumoDeSenha:
    return GeradorDeResumoArgon2()


def obter_emissor_de_sessao() -> EmissorDeSessao:
    return EmissorDeSessaoJwt(
        chave=configuracao.chave_da_sessao,
        validade=timedelta(hours=configuracao.validade_da_sessao_em_horas),
    )


def recusar_sessao() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="sessão ausente, vencida ou inválida",
        headers={"WWW-Authenticate": "Bearer"},
    )


def obter_usuario_da_sessao(
    sessao: SessaoDoBanco,
    emissor_de_sessao: Annotated[EmissorDeSessao, Depends(obter_emissor_de_sessao)],
    credenciais: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
) -> Usuario:
    """Aceita senha provisória. A situação do usuário é lida do banco a cada requisição."""
    if credenciais is None:
        raise recusar_sessao()
    try:
        usuario = criar_usuarios(sessao).obter(emissor_de_sessao.ler(credenciais.credentials))
    except SessaoInvalida, UsuarioNaoEncontrado:
        raise recusar_sessao() from None
    if usuario.situacao is not SituacaoDoUsuario.ATIVO:
        raise recusar_sessao()
    return usuario


def exigir_senha_definitiva(
    usuario: Annotated[Usuario, Depends(obter_usuario_da_sessao)],
) -> UsuarioAutenticado:
    """Padrão das rotas: com senha provisória, só "quem sou eu" e "trocar senha" funcionam."""
    if usuario.senha_provisoria:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="troque a senha provisória antes de continuar",
        )
    return UsuarioAutenticado.de(usuario)


UsuarioDaSessao = Annotated[Usuario, Depends(obter_usuario_da_sessao)]
UsuarioComSenhaDefinitiva = Annotated[UsuarioAutenticado, Depends(exigir_senha_definitiva)]
GeradorDeResumo = Annotated[GeradorDeResumoDeSenha, Depends(obter_gerador_de_resumo)]


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


class DadosDeRedefinicaoDeSenha(BaseModel):
    senha_provisoria: str


roteador_de_autenticacao = APIRouter(prefix="/autenticacao", tags=["autenticação"])
roteador_de_usuarios = APIRouter(prefix="/usuarios", tags=["usuários"])


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
    sessao: SessaoDoBanco,
    gerador_de_resumo: GeradorDeResumo,
) -> None:
    TrocarPropriaSenha(
        criar_usuarios(sessao), gerador_de_resumo, RegistrarAcao(criar_historico(sessao))
    ).executar(usuario_id=usuario.id, senha_atual=dados.senha_atual, nova_senha=dados.nova_senha)
    sessao.commit()


@roteador_de_usuarios.post("/{usuario_id}/senha", status_code=status.HTTP_204_NO_CONTENT)
def redefinir_a_senha(
    usuario_id: UUID,
    dados: DadosDeRedefinicaoDeSenha,
    solicitante: UsuarioComSenhaDefinitiva,
    sessao: SessaoDoBanco,
    gerador_de_resumo: GeradorDeResumo,
) -> None:
    RedefinirSenha(
        criar_usuarios(sessao), gerador_de_resumo, RegistrarAcao(criar_historico(sessao))
    ).executar(
        solicitante=solicitante, usuario_id=usuario_id, senha_provisoria=dados.senha_provisoria
    )
    sessao.commit()


def responder_erro_de_identidade(_: Request, erro: Exception) -> JSONResponse:
    situacao = STATUS_POR_ERRO.get(type(erro), status.HTTP_422_UNPROCESSABLE_CONTENT)
    return JSONResponse(status_code=situacao, content={"detail": str(erro)})


def registrar_rotas_de_identidade(app: FastAPI) -> None:
    app.include_router(roteador_de_autenticacao)
    app.include_router(roteador_de_usuarios)
    app.add_exception_handler(ErroDeIdentidade, responder_erro_de_identidade)
