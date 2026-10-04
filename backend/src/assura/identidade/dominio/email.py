import re
from dataclasses import dataclass
from typing import Self

from assura.identidade.dominio.erros import EmailInvalido

TAMANHO_MAXIMO_DE_EMAIL = 254
# Validação só estrutural: a prova de que um e-mail existe é ele receber mensagens.
FORMATO_DO_EMAIL = re.compile(r"[^@\s]+@[^@\s.]+(\.[^@\s.]+)+")


@dataclass(frozen=True)
class Email:
    valor: str

    def __post_init__(self) -> None:
        if len(self.valor) > TAMANHO_MAXIMO_DE_EMAIL or not FORMATO_DO_EMAIL.fullmatch(self.valor):
            raise EmailInvalido(f"e-mail inválido: {self.valor!r}")
        if self.valor != self.valor.lower():
            raise EmailInvalido("o e-mail é guardado em letras minúsculas")

    @classmethod
    def criar(cls, texto: str) -> Self:
        return cls(texto.strip().lower())
