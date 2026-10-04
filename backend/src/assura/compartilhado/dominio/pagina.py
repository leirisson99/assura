from dataclasses import dataclass

TAMANHO_DE_PAGINA_PADRAO = 50
TAMANHO_DE_PAGINA_MAXIMO = 200


class PaginaInvalida(Exception):
    pass


@dataclass(frozen=True)
class Pagina:
    numero: int = 1
    tamanho: int = TAMANHO_DE_PAGINA_PADRAO

    def __post_init__(self) -> None:
        if self.numero < 1:
            raise PaginaInvalida("o número da página começa em 1")
        if not 1 <= self.tamanho <= TAMANHO_DE_PAGINA_MAXIMO:
            raise PaginaInvalida(f"o tamanho da página vai de 1 a {TAMANHO_DE_PAGINA_MAXIMO}")

    @property
    def deslocamento(self) -> int:
        return (self.numero - 1) * self.tamanho
