from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from assura.compartilhado.dominio.pagina import Pagina
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa
from assura.identidade.dominio.usuario import Usuario
from assura.identidade.dominio.vinculo import SituacaoDoVinculo, Vinculo


class Empresas(Protocol):
    """Armazenamento de empresas: não existe operação de excluir (Princípio III)."""

    def adicionar(self, empresa: Empresa) -> None:
        """Recusa CNPJ repetido com CnpjJaCadastrado, mesmo em gravações simultâneas."""
        ...

    def atualizar(self, empresa: Empresa) -> None:
        """Recusa CNPJ repetido com CnpjJaCadastrado, mesmo em gravações simultâneas."""
        ...

    def obter(self, empresa_id: UUID) -> Empresa:
        """Recusa identificador inexistente com EmpresaNaoEncontrada."""
        ...

    def existe_cnpj(self, cnpj: Cnpj, exceto_empresa_id: UUID | None = None) -> bool: ...

    def listar(self, situacao: SituacaoDaEmpresa | None, pagina: Pagina) -> list[Empresa]:
        """Ordem alfabética de razão social; situação nenhuma lista todas."""
        ...


class Usuarios(Protocol):
    """Armazenamento de usuários: não existe operação de excluir (Princípio III)."""

    def adicionar(self, usuario: Usuario) -> None:
        """Recusa e-mail repetido com EmailJaCadastrado, mesmo em gravações simultâneas."""
        ...

    def atualizar(self, usuario: Usuario) -> None:
        """Recusa e-mail repetido com EmailJaCadastrado, mesmo em gravações simultâneas."""
        ...

    def obter(self, usuario_id: UUID) -> Usuario:
        """Recusa identificador inexistente com UsuarioNaoEncontrado."""
        ...

    def existe_email(self, email: Email, exceto_usuario_id: UUID | None = None) -> bool: ...

    def obter_por_email(self, email: Email) -> Usuario | None: ...

    def existe_administrador_do_sistema(self) -> bool: ...


@dataclass(frozen=True)
class UsuarioDaEmpresa:
    usuario: Usuario
    vinculo: Vinculo


class Vinculos(Protocol):
    """Armazenamento de vínculos: não existe operação de excluir (Princípio III)."""

    def adicionar(self, vinculo: Vinculo) -> None:
        """Recusa segundo vínculo do mesmo par com VinculoJaExiste, mesmo simultâneo."""
        ...

    def atualizar(self, vinculo: Vinculo) -> None: ...

    def obter(self, vinculo_id: UUID) -> Vinculo:
        """Recusa identificador inexistente com VinculoNaoEncontrado."""
        ...

    def existe(self, usuario_id: UUID, empresa_id: UUID) -> bool: ...

    def listar_da_empresa(
        self, empresa_id: UUID, situacao: SituacaoDoVinculo | None, pagina: Pagina
    ) -> list[UsuarioDaEmpresa]:
        """Só os vínculos da empresa pedida, em ordem alfabética do nome do usuário."""
        ...


class GeradorDeResumoDeSenha(Protocol):
    def gerar(self, senha: str) -> str: ...

    def conferir(self, resumo: str, senha: str) -> bool:
        """Falso para senha errada ou resumo inválido; nunca levanta erro."""
        ...


@dataclass(frozen=True)
class SessaoEmitida:
    token: str
    expira_em: datetime


class EmissorDeSessao(Protocol):
    def emitir(self, usuario_id: UUID) -> SessaoEmitida: ...

    def ler(self, token: str) -> UUID:
        """Devolve o usuário da sessão ou recusa com SessaoInvalida (vencida, adulterada...)."""
        ...


@dataclass(frozen=True)
class UsuarioAutenticado:
    """O que as regras de permissão precisam saber de quem está usando o sistema."""

    id: UUID
    administrador_do_sistema: bool
    senha_provisoria: bool

    @classmethod
    def de(cls, usuario: Usuario) -> UsuarioAutenticado:
        return cls(
            id=usuario.id,
            administrador_do_sistema=usuario.administrador_do_sistema,
            senha_provisoria=usuario.senha_provisoria,
        )
