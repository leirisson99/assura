class ErroDeIdentidade(Exception):
    """Base dos erros de negócio do contexto de identidade e acesso."""


class CnpjInvalido(ErroDeIdentidade):
    pass


class CnpjJaCadastrado(ErroDeIdentidade):
    pass


class RazaoSocialInvalida(ErroDeIdentidade):
    pass


class NomeFantasiaInvalido(ErroDeIdentidade):
    pass


class EmpresaNaoEncontrada(ErroDeIdentidade):
    pass


class EmpresaJaDesativada(ErroDeIdentidade):
    pass


class EmpresaJaAtiva(ErroDeIdentidade):
    pass
