"""Interface pública do contexto de identidade e acesso.

Outros contextos usam apenas o que é exportado aqui, nunca as tabelas diretamente.
"""

from assura.identidade.aplicacao.alterar_empresa import AlterarEmpresa
from assura.identidade.aplicacao.alterar_usuario import AlterarUsuario
from assura.identidade.aplicacao.cadastrar_empresa import CadastrarEmpresa
from assura.identidade.aplicacao.cadastrar_usuario import CadastrarUsuario
from assura.identidade.aplicacao.consultar_empresas import ConsultarEmpresas
from assura.identidade.aplicacao.consultar_usuarios import ConsultarUsuarios
from assura.identidade.aplicacao.mudar_situacao_da_empresa import DesativarEmpresa, ReativarEmpresa
from assura.identidade.aplicacao.mudar_situacao_do_vinculo import DesativarVinculo, ReativarVinculo
from assura.identidade.aplicacao.portas import Empresas, UsuarioDaEmpresa, Usuarios, Vinculos
from assura.identidade.aplicacao.vincular_usuario import VincularUsuario
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.email import Email
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa
from assura.identidade.dominio.erros import (
    CnpjInvalido,
    CnpjJaCadastrado,
    EmailInvalido,
    EmailJaCadastrado,
    EmpresaDesativadaNaoAceitaVinculo,
    EmpresaJaAtiva,
    EmpresaJaDesativada,
    EmpresaNaoEncontrada,
    ErroDeIdentidade,
    NomeDeUsuarioInvalido,
    NomeFantasiaInvalido,
    RazaoSocialInvalida,
    UsuarioNaoEncontrado,
    VinculoJaAtivo,
    VinculoJaDesativado,
    VinculoJaExiste,
    VinculoNaoEncontrado,
)
from assura.identidade.dominio.usuario import SituacaoDoUsuario, Usuario
from assura.identidade.dominio.vinculo import SituacaoDoVinculo, Vinculo
from assura.identidade.infraestrutura.empresas_sqlalchemy import criar_empresas
from assura.identidade.infraestrutura.usuarios_sqlalchemy import criar_usuarios
from assura.identidade.infraestrutura.vinculos_sqlalchemy import criar_vinculos

__all__ = [
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
