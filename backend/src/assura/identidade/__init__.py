"""Interface pública do contexto de identidade e acesso.

Outros contextos usam apenas o que é exportado aqui, nunca as tabelas diretamente.
"""

from assura.identidade.aplicacao.administrador_da_empresa import (
    RemoverAdministrador,
    TornarAdministrador,
)
from assura.identidade.aplicacao.alterar_empresa import AlterarEmpresa
from assura.identidade.aplicacao.alterar_usuario import AlterarUsuario
from assura.identidade.aplicacao.autenticar import Autenticar
from assura.identidade.aplicacao.cadastrar_empresa import CadastrarEmpresa
from assura.identidade.aplicacao.cadastrar_usuario import CadastrarUsuario
from assura.identidade.aplicacao.consultar_empresas import ConsultarEmpresas
from assura.identidade.aplicacao.consultar_usuarios import ConsultarUsuarios
from assura.identidade.aplicacao.criar_root import CriarRoot
from assura.identidade.aplicacao.incluir_usuario_na_empresa import IncluirUsuarioNaEmpresa
from assura.identidade.aplicacao.mudar_situacao_da_empresa import DesativarEmpresa, ReativarEmpresa
from assura.identidade.aplicacao.mudar_situacao_do_vinculo import DesativarVinculo, ReativarVinculo
from assura.identidade.aplicacao.permissoes import Permissoes
from assura.identidade.aplicacao.portas import (
    Empresas,
    UsuarioAutenticado,
    UsuarioDaEmpresa,
    Usuarios,
    Vinculos,
)
from assura.identidade.aplicacao.redefinir_senha import RedefinirSenha
from assura.identidade.aplicacao.trocar_propria_senha import TrocarPropriaSenha
from assura.identidade.aplicacao.vincular_usuario import VincularUsuario
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa
from assura.identidade.dominio.erros import (
    AdministradorDoSistemaJaExiste,
    CnpjInvalido,
    CnpjJaCadastrado,
    CredenciaisInvalidas,
    EmailInvalido,
    EmailJaCadastrado,
    EmpresaDesativadaNaoAceitaVinculo,
    EmpresaJaAtiva,
    EmpresaJaDesativada,
    EmpresaNaoEncontrada,
    ErroDeIdentidade,
    NomeDeUsuarioInvalido,
    NomeFantasiaInvalido,
    PermissaoNegada,
    RazaoSocialInvalida,
    SenhaAtualIncorreta,
    SenhaInvalida,
    SenhaProvisoriaPrecisaSerTrocada,
    SessaoInvalida,
    UltimoAdministradorNaoPodeSerRemovido,
    UsuarioNaoEncontrado,
    VinculoDesativadoNaoPodeSerAdministrador,
    VinculoJaAtivo,
    VinculoJaDesativado,
    VinculoJaEAdministrador,
    VinculoJaExiste,
    VinculoNaoEAdministrador,
    VinculoNaoEncontrado,
)
from assura.identidade.dominio.usuario import SituacaoDoUsuario, Usuario
from assura.identidade.dominio.vinculo import SituacaoDoVinculo, Vinculo
from assura.identidade.infraestrutura.empresas_sqlalchemy import criar_empresas
from assura.identidade.infraestrutura.usuarios_sqlalchemy import criar_usuarios
from assura.identidade.infraestrutura.vinculos_sqlalchemy import criar_vinculos

__all__ = [
    "RemoverAdministrador",
    "TornarAdministrador",
    "IncluirUsuarioNaEmpresa",
    "Permissoes",
    "UltimoAdministradorNaoPodeSerRemovido",
    "VinculoDesativadoNaoPodeSerAdministrador",
    "VinculoJaEAdministrador",
    "VinculoNaoEAdministrador",
    "Autenticar",
    "CriarRoot",
    "UsuarioAutenticado",
    "RedefinirSenha",
    "TrocarPropriaSenha",
    "AdministradorDoSistemaJaExiste",
    "CredenciaisInvalidas",
    "PermissaoNegada",
    "SenhaAtualIncorreta",
    "SenhaInvalida",
    "SenhaProvisoriaPrecisaSerTrocada",
    "SessaoInvalida",
    "AlterarEmpresa",
    "AlterarUsuario",
    "CadastrarEmpresa",
    "CadastrarUsuario",
    "Cnpj",
    "CnpjInvalido",
    "CnpjJaCadastrado",
    "ConsultarEmpresas",
    "ConsultarUsuarios",
    "DesativarEmpresa",
    "DesativarVinculo",
    "Email",
    "EmailInvalido",
    "EmailJaCadastrado",
    "Empresa",
    "EmpresaDesativadaNaoAceitaVinculo",
    "EmpresaJaAtiva",
    "EmpresaJaDesativada",
    "EmpresaNaoEncontrada",
    "Empresas",
    "ErroDeIdentidade",
    "NomeDeUsuarioInvalido",
    "NomeFantasiaInvalido",
    "RazaoSocialInvalida",
    "ReativarEmpresa",
    "ReativarVinculo",
    "SituacaoDaEmpresa",
    "SituacaoDoUsuario",
    "SituacaoDoVinculo",
    "Usuario",
    "UsuarioDaEmpresa",
    "UsuarioNaoEncontrado",
    "Usuarios",
    "VincularUsuario",
    "Vinculo",
    "VinculoJaAtivo",
    "VinculoJaDesativado",
    "VinculoJaExiste",
    "VinculoNaoEncontrado",
    "Vinculos",
    "criar_empresas",
    "criar_usuarios",
    "criar_vinculos",
]
