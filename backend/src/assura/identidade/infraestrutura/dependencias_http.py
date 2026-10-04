from dataclasses import dataclass
from datetime import timedelta
from functools import cache
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from assura.compartilhado.dominio.pagina import Pagina
from assura.compartilhado.infraestrutura.http import SessaoDoBanco
from assura.configuracao import configuracao
from assura.historico import RegistrarAcao, criar_historico
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import (
    EmissorDeSessao,
    Empresas,
    GeradorDeResumoDeSenha,
    UsuarioAutenticado,
    Usuarios,
    Vinculos,
)
from assura.identidade.dominio.erros import SessaoInvalida, UsuarioNaoEncontrado
from assura.identidade.dominio.usuario import SituacaoDoUsuario, Usuario
from assura.identidade.infraestrutura.empresas_sqlalchemy import criar_empresas
from assura.identidade.infraestrutura.resumo_de_senha_argon2 import GeradorDeResumoArgon2
from assura.identidade.infraestrutura.sessao_jwt import EmissorDeSessaoJwt
from assura.identidade.infraestrutura.usuarios_sqlalchemy import criar_usuarios
from assura.identidade.infraestrutura.vinculos_sqlalchemy import criar_vinculos

esquema_bearer = HTTPBearer(auto_error=False)


@cache
def obter_gerador_de_resumo() -> GeradorDeResumoDeSenha:
    return GeradorDeResumoArgon2()


def obter_emissor_de_sessao() -> EmissorDeSessao:
    return EmissorDeSessaoJwt(
        chave=configuracao.chave_da_sessao,
        validade=timedelta(hours=configuracao.validade_da_sessao_em_horas),
    )


@dataclass(frozen=True)
class Repositorios:
    """O que os casos de uso de identidade usam, ligado à sessão do banco da requisição."""

    sessao: Session
    usuarios: Usuarios
    empresas: Empresas
    vinculos: Vinculos
    permissoes: Permissoes
    registrar_acao: RegistrarAcao


def obter_repositorios(sessao: SessaoDoBanco) -> Repositorios:
    empresas, vinculos = criar_empresas(sessao), criar_vinculos(sessao)
    return Repositorios(
        sessao=sessao,
        usuarios=criar_usuarios(sessao),
        empresas=empresas,
        vinculos=vinculos,
        permissoes=Permissoes(vinculos, empresas),
        registrar_acao=RegistrarAcao(criar_historico(sessao)),
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


def ler_pagina(numero: int = 1, tamanho: int = 50) -> Pagina:
    return Pagina(numero=numero, tamanho=tamanho)


UsuarioDaSessao = Annotated[Usuario, Depends(obter_usuario_da_sessao)]
Solicitante = Annotated[UsuarioAutenticado, Depends(exigir_senha_definitiva)]
RepositoriosDaRequisicao = Annotated[Repositorios, Depends(obter_repositorios)]
GeradorDeResumo = Annotated[GeradorDeResumoDeSenha, Depends(obter_gerador_de_resumo)]
PaginaPedida = Annotated[Pagina, Depends(ler_pagina)]
