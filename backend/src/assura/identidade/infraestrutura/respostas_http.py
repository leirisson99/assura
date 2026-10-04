from typing import Self
from uuid import UUID

from pydantic import BaseModel

from assura.identidade.aplicacao.portas import UsuarioDaEmpresa
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa
from assura.identidade.dominio.usuario import SituacaoDoUsuario, Usuario
from assura.identidade.dominio.vinculo import SituacaoDoVinculo, Vinculo


class EmpresaResposta(BaseModel):
    id: UUID
    razao_social: str
    nome_fantasia: str | None
    cnpj: str
    cnpj_formatado: str
    situacao: SituacaoDaEmpresa

    @classmethod
    def de(cls, empresa: Empresa) -> Self:
        return cls(
            id=empresa.id,
            razao_social=empresa.razao_social,
            nome_fantasia=empresa.nome_fantasia,
            cnpj=empresa.cnpj.valor,
            cnpj_formatado=empresa.cnpj.formatado,
            situacao=empresa.situacao,
        )


class UsuarioResposta(BaseModel):
    """Nunca inclui o resumo da senha."""

    id: UUID
    nome: str
    email: str
    situacao: SituacaoDoUsuario
    administrador_do_sistema: bool

    @classmethod
    def de(cls, usuario: Usuario) -> Self:
        return cls(
            id=usuario.id,
            nome=usuario.nome,
            email=usuario.email.valor,
            situacao=usuario.situacao,
            administrador_do_sistema=usuario.administrador_do_sistema,
        )


class VinculoResposta(BaseModel):
    id: UUID
    usuario_id: UUID
    empresa_id: UUID
    situacao: SituacaoDoVinculo
    administrador_da_empresa: bool

    @classmethod
    def de(cls, vinculo: Vinculo) -> Self:
        return cls(
            id=vinculo.id,
            usuario_id=vinculo.usuario_id,
            empresa_id=vinculo.empresa_id,
            situacao=vinculo.situacao,
            administrador_da_empresa=vinculo.administrador_da_empresa,
        )


class UsuarioDaEmpresaResposta(BaseModel):
    usuario: UsuarioResposta
    vinculo: VinculoResposta

    @classmethod
    def de(cls, usuario_da_empresa: UsuarioDaEmpresa) -> Self:
        return cls(
            usuario=UsuarioResposta.de(usuario_da_empresa.usuario),
            vinculo=VinculoResposta.de(usuario_da_empresa.vinculo),
        )
