import re
from dataclasses import dataclass
from typing import Self

from assura.identidade.dominio.erros import CnpjInvalido

CARACTERES_DA_MASCARA = str.maketrans("", "", "./-")
# 12 caracteres de raiz e ordem (letras maiúsculas ou números, desde o CNPJ alfanumérico de
# julho de 2026) seguidos de 2 dígitos verificadores, sempre numéricos.
FORMATO_DO_CNPJ = re.compile(r"[0-9A-Z]{12}[0-9]{2}")
PESOS_DO_PRIMEIRO_DIGITO = (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
PESOS_DO_SEGUNDO_DIGITO = (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)
# Regra da Receita: cada caractere vale o seu código ASCII menos 48 ("0" vale 0, "A" vale 17).
CODIGO_DO_ZERO = ord("0")


def calcular_digito_verificador(caracteres: str, pesos: tuple[int, ...]) -> str:
    soma = sum(
        (ord(caractere) - CODIGO_DO_ZERO) * peso
        for caractere, peso in zip(caracteres, pesos, strict=True)
    )
    resto = soma % 11
    return "0" if resto < 2 else str(11 - resto)


def calcular_digitos_verificadores(raiz_e_ordem: str) -> str:
    primeiro = calcular_digito_verificador(raiz_e_ordem, PESOS_DO_PRIMEIRO_DIGITO)
    segundo = calcular_digito_verificador(raiz_e_ordem + primeiro, PESOS_DO_SEGUNDO_DIGITO)
    return primeiro + segundo


@dataclass(frozen=True)
class Cnpj:
    valor: str

    def __post_init__(self) -> None:
        if not FORMATO_DO_CNPJ.fullmatch(self.valor):
            raise CnpjInvalido(f"CNPJ fora do formato: {self.valor!r}")
        if len(set(self.valor)) == 1:
            raise CnpjInvalido("CNPJ com um só caractere repetido")
        if calcular_digitos_verificadores(self.valor[:12]) != self.valor[12:]:
            raise CnpjInvalido(f"dígitos verificadores do CNPJ não conferem: {self.valor!r}")

    @classmethod
    def criar(cls, texto: str) -> Self:
        return cls(texto.strip().translate(CARACTERES_DA_MASCARA).upper())

    @property
    def formatado(self) -> str:
        valor = self.valor
        return f"{valor[:2]}.{valor[2:5]}.{valor[5:8]}/{valor[8:12]}-{valor[12:]}"
