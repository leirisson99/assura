from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from assura.identidade.aplicacao.alterar_usuario import AlterarUsuario
from assura.identidade.aplicacao.consultar_usuarios import ConsultarUsuarios
from assura.identidade.aplicacao.redefinir_senha import RedefinirSenha
from assura.identidade.infraestrutura.dependencias_http import (
    GeradorDeResumo,
    RepositoriosDaRequisicao,
    Solicitante,
)
from assura.identidade.infraestrutura.respostas_http import UsuarioResposta

roteador_de_usuarios = APIRouter(prefix="/usuarios", tags=["usuários"])


class DadosDoUsuario(BaseModel):
    nome: str
    email: str


class DadosDeRedefinicaoDeSenha(BaseModel):
    senha_provisoria: str


@roteador_de_usuarios.get("/{usuario_id}")
def obter_usuario(
    usuario_id: UUID, solicitante: Solicitante, repositorios: RepositoriosDaRequisicao
) -> UsuarioResposta:
    usuario = ConsultarUsuarios(
        repositorios.usuarios, repositorios.vinculos, repositorios.permissoes
    ).obter(solicitante=solicitante, usuario_id=usuario_id)
    return UsuarioResposta.de(usuario)


@roteador_de_usuarios.put("/{usuario_id}")
def alterar_usuario(
    usuario_id: UUID,
    dados: DadosDoUsuario,
    solicitante: Solicitante,
    repositorios: RepositoriosDaRequisicao,
) -> UsuarioResposta:
    usuario = AlterarUsuario(repositorios.usuarios, repositorios.registrar_acao).executar(
        solicitante=solicitante, usuario_id=usuario_id, nome=dados.nome, email=dados.email
    )
    repositorios.sessao.commit()
    return UsuarioResposta.de(usuario)


@roteador_de_usuarios.post("/{usuario_id}/senha", status_code=status.HTTP_204_NO_CONTENT)
def redefinir_a_senha(
    usuario_id: UUID,
    dados: DadosDeRedefinicaoDeSenha,
    solicitante: Solicitante,
    repositorios: RepositoriosDaRequisicao,
    gerador_de_resumo: GeradorDeResumo,
) -> None:
    RedefinirSenha(
        repositorios.usuarios,
        repositorios.permissoes,
        gerador_de_resumo,
        repositorios.registrar_acao,
    ).executar(
        solicitante=solicitante, usuario_id=usuario_id, senha_provisoria=dados.senha_provisoria
    )
    repositorios.sessao.commit()
