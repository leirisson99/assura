from uuid import UUID

from assura.historico import Autor, Detalhes, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_da_empresa import registrar_acao_sobre_empresa
from assura.identidade.aplicacao.permissoes import exigir_administrador_do_sistema
from assura.identidade.aplicacao.portas import Empresas, UsuarioAutenticado
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.empresa import Empresa
from assura.identidade.dominio.erros import CnpjJaCadastrado


class AlterarEmpresa:
    """Substitui os dados da empresa; sem mudança efetiva, nada é gravado nem registrado."""

    def __init__(self, empresas: Empresas, registrar_acao: RegistrarAcao) -> None:
        self._empresas = empresas
        self._registrar_acao = registrar_acao

    def executar(
        self,
        *,
        solicitante: UsuarioAutenticado,
        empresa_id: UUID,
        razao_social: str,
        nome_fantasia: str | None,
        cnpj: str,
    ) -> Empresa:
        exigir_administrador_do_sistema(solicitante)
        empresa = self._empresas.obter(empresa_id)
        novo_cnpj = Cnpj.criar(cnpj)
        if self._empresas.existe_cnpj(novo_cnpj, exceto_empresa_id=empresa.id):
            raise CnpjJaCadastrado(f"já existe outra empresa com o CNPJ {novo_cnpj.formatado}")
        alteracoes = empresa.alterar_dados(
            razao_social=razao_social, nome_fantasia=nome_fantasia, cnpj=novo_cnpj
        )
        if not alteracoes:
            return empresa
        self._empresas.atualizar(empresa)
        detalhes: Detalhes = {
            campo: {"anterior": alteracao["anterior"], "novo": alteracao["novo"]}
            for campo, alteracao in alteracoes.items()
        }
        registrar_acao_sobre_empresa(
            self._registrar_acao,
            autor=Autor.usuario(solicitante.id),
            tipo_de_acao=TipoDeAcao.EMPRESA_ALTERADA,
            empresa_id=empresa.id,
            detalhes=detalhes,
        )
        return empresa
