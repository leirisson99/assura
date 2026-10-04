from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError


class GeradorDeResumoArgon2:
    """argon2id com os parâmetros padrão da biblioteca, recomendados pela OWASP."""

    def __init__(self) -> None:
        self._gerador = PasswordHasher()

    def gerar(self, senha: str) -> str:
        return self._gerador.hash(senha)

    def conferir(self, resumo: str, senha: str) -> bool:
        try:
            return self._gerador.verify(resumo, senha)
        except VerificationError, InvalidHashError:
            return False
