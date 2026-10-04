from assura.identidade.dominio.erros import SenhaInvalida

# NIST SP 800-63B: tamanho mínimo, máximo generoso e nenhuma regra de composição.
TAMANHO_MINIMO_DE_SENHA = 8
TAMANHO_MAXIMO_DE_SENHA = 128


def validar_senha(senha: str) -> str:
    """Devolve a senha como digitada (espaços inclusive) ou recusa com SenhaInvalida."""
    if not TAMANHO_MINIMO_DE_SENHA <= len(senha) <= TAMANHO_MAXIMO_DE_SENHA:
        raise SenhaInvalida(
            f"a senha tem de {TAMANHO_MINIMO_DE_SENHA} a {TAMANHO_MAXIMO_DE_SENHA} caracteres"
        )
    return senha
