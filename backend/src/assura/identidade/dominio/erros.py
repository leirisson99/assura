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


class EmailInvalido(ErroDeIdentidade):
    pass


class EmailJaCadastrado(ErroDeIdentidade):
    pass


class NomeDeUsuarioInvalido(ErroDeIdentidade):
    pass


class UsuarioNaoEncontrado(ErroDeIdentidade):
    pass


class VinculoJaExiste(ErroDeIdentidade):
    pass


class VinculoNaoEncontrado(ErroDeIdentidade):
    pass


class VinculoJaDesativado(ErroDeIdentidade):
    pass


class VinculoJaAtivo(ErroDeIdentidade):
    pass


class EmpresaDesativadaNaoAceitaVinculo(ErroDeIdentidade):
    pass


class SenhaInvalida(ErroDeIdentidade):
    pass


class CredenciaisInvalidas(ErroDeIdentidade):
    pass


class SenhaAtualIncorreta(ErroDeIdentidade):
    pass


class PermissaoNegada(ErroDeIdentidade):
    pass


class SenhaProvisoriaPrecisaSerTrocada(ErroDeIdentidade):
    pass


class AdministradorDoSistemaJaExiste(ErroDeIdentidade):
    pass


class SessaoInvalida(ErroDeIdentidade):
    pass


class VinculoDesativadoNaoPodeSerAdministrador(ErroDeIdentidade):
    pass


class VinculoJaEAdministrador(ErroDeIdentidade):
    pass


class VinculoNaoEAdministrador(ErroDeIdentidade):
    pass


class UltimoAdministradorNaoPodeSerRemovido(ErroDeIdentidade):
    pass


class UsuarioJaDesativado(ErroDeIdentidade):
    pass


class UsuarioJaAtivo(ErroDeIdentidade):
    pass


class UltimoAdministradorDoSistemaNaoPodeSerDesativado(ErroDeIdentidade):
    pass
