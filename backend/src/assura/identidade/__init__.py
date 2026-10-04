"""Interface pública do contexto de identidade e acesso.

Outros contextos usam apenas o que é exportado aqui, nunca as tabelas diretamente.
"""

from assura.identidade.aplicacao.alterar_empresa import AlterarEmpresa
from assura.identidade.aplicacao.cadastrar_empresa import CadastrarEmpresa
from assura.identidade.aplicacao.consultar_empresas import ConsultarEmpresas
from assura.identidade.aplicacao.mudar_situacao_da_empresa import DesativarEmpresa, ReativarEmpresa
from assura.identidade.aplicacao.portas import Empresas
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa
from assura.identidade.dominio.erros import (
    CnpjInvalido,
    CnpjJaCadastrado,
    EmpresaJaAtiva,
    EmpresaJaDesativada,
    EmpresaNaoEncontrada,
    ErroDeIdentidade,
    NomeFantasiaInvalido,
    RazaoSocialInvalida,
)
from assura.identidade.infraestrutura.empresas_sqlalchemy import criar_empresas

__all__ = [
    "AlterarEmpresa",
    "CadastrarEmpresa",
    "Cnpj",
    "CnpjInvalido",
    "CnpjJaCadastrado",
    "ConsultarEmpresas",
    "DesativarEmpresa",
    "Empresa",
    "EmpresaJaAtiva",
    "EmpresaJaDesativada",
    "EmpresaNaoEncontrada",
    "Empresas",
    "ErroDeIdentidade",
    "NomeFantasiaInvalido",
    "RazaoSocialInvalida",
    "ReativarEmpresa",
    "SituacaoDaEmpresa",
    "criar_empresas",
]
