from assura.historico import Autor, RegistrarAcao, TipoDeAcao
from assura.identidade.aplicacao.historico_da_empresa import registrar_acao_sobre_empresa
from assura.identidade.aplicacao.portas import Empresas
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.empresa import Empresa
from assura.identidade.dominio.erros import CnpjJaCadastrado


class CadastrarEmpresa:
    """Cadastra a empresa e registra a ação na transação de quem chama, sem confirmá-la."""

    def __init__(self, empresas: Empresas, registrar_acao: RegistrarAcao) -> None:
        self._empresas = empresas
        self._registrar_acao = registrar_acao

    def executar(
        self, *, autor: Autor, razao_social: str, nome_fantasia: str | None, cnpj: str
    ) -> Empresa:
        empresa = Empresa.cadastrar(
            razao_social=razao_social, nome_fantasia=nome_fantasia, cnpj=Cnpj.criar(cnpj)
        )
        if self._empresas.existe_cnpj(empresa.cnpj):
            raise CnpjJaCadastrado(f"já existe empresa com o CNPJ {empresa.cnpj.formatado}")
        self._empresas.adicionar(empresa)
        registrar_acao_sobre_empresa(
            self._registrar_acao,
            autor=autor,
            tipo_de_acao=TipoDeAcao.EMPRESA_CADASTRADA,
            empresa_id=empresa.id,
            detalhes={
                "razao_social": empresa.razao_social,
                "nome_fantasia": empresa.nome_fantasia,
                "cnpj": empresa.cnpj.valor,
            },
        )
        return empresa
