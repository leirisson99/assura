from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from assura.identidade.aplicacao.portas import SessaoEmitida
from assura.identidade.dominio.erros import SessaoInvalida

ALGORITMO = "HS256"


def ler_relogio_do_servidor() -> datetime:
    return datetime.now(UTC)


class EmissorDeSessaoJwt:
    """O token só identifica o usuário; situação e permissões são lidas do banco a cada uso."""

    def __init__(
        self,
        *,
        chave: str,
        validade: timedelta,
        relogio: Callable[[], datetime] = ler_relogio_do_servidor,
    ) -> None:
        self._chave = chave
        self._validade = validade
        self._relogio = relogio

    def emitir(self, usuario_id: UUID) -> SessaoEmitida:
        agora = self._relogio()
        expira_em = agora + self._validade
        token = jwt.encode(
            {"sub": str(usuario_id), "iat": agora, "exp": expira_em},
            self._chave,
            algorithm=ALGORITMO,
        )
        return SessaoEmitida(token=token, expira_em=expira_em)

    def ler(self, token: str) -> UUID:
        try:
            conteudo = jwt.decode(
                token,
                self._chave,
                algorithms=[ALGORITMO],
                options={"require": ["sub", "exp", "iat"], "verify_exp": False},
            )
            usuario_id = UUID(conteudo["sub"])
        except (jwt.InvalidTokenError, ValueError) as erro:
            raise SessaoInvalida("sessão inválida") from erro
        # A validade é conferida com o relógio injetado (e não o do PyJWT) para poder ser testada.
        if self._relogio().timestamp() >= conteudo["exp"]:
            raise SessaoInvalida("sessão vencida")
        return usuario_id
