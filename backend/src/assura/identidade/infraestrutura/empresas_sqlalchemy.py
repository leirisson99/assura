from typing import Any
from uuid import UUID

from sqlalchemy import Executable, RowMapping, exists, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from assura.compartilhado.dominio.pagina import Pagina
from assura.identidade.aplicacao.portas import Empresas
from assura.identidade.dominio.cnpj import Cnpj
from assura.identidade.dominio.empresa import Empresa, SituacaoDaEmpresa
from assura.identidade.dominio.erros import CnpjJaCadastrado, EmpresaNaoEncontrada
from assura.identidade.infraestrutura.tabela import tabela_empresa

colunas = tabela_empresa.c
RESTRICAO_DE_CNPJ_UNICO = "uq_empresa_cnpj"


class EmpresasSqlAlchemy:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, empresa: Empresa) -> None:
        self._gravar(insert(tabela_empresa).values(id=empresa.id, **converter_em_colunas(empresa)))

    def atualizar(self, empresa: Empresa) -> None:
        self._gravar(
            update(tabela_empresa)
            .where(colunas.id == empresa.id)
            .values(**converter_em_colunas(empresa))
        )

    def obter(self, empresa_id: UUID) -> Empresa:
        linha = (
            self._sessao.execute(select(tabela_empresa).where(colunas.id == empresa_id))
            .mappings()
            .one_or_none()
        )
        if linha is None:
            raise EmpresaNaoEncontrada(f"empresa {empresa_id} não encontrada")
        return converter_em_empresa(linha)

    def existe_cnpj(self, cnpj: Cnpj, exceto_empresa_id: UUID | None = None) -> bool:
        condicao = colunas.cnpj == cnpj.valor
        if exceto_empresa_id is not None:
            condicao = condicao & (colunas.id != exceto_empresa_id)
        return bool(self._sessao.scalar(select(exists().where(condicao))))

    def listar(self, situacao: SituacaoDaEmpresa | None, pagina: Pagina) -> list[Empresa]:
        consulta = select(tabela_empresa)
        if situacao is not None:
            consulta = consulta.where(colunas.situacao == str(situacao))
        consulta = (
            consulta.order_by(func.lower(colunas.razao_social), colunas.id)
            .limit(pagina.tamanho)
            .offset(pagina.deslocamento)
        )
        return [converter_em_empresa(linha) for linha in self._sessao.execute(consulta).mappings()]

    def _gravar(self, comando: Executable) -> None:
        # O savepoint mantém a transação de quem chama utilizável quando o banco recusa o CNPJ.
        try:
            with self._sessao.begin_nested():
                self._sessao.execute(comando)
        except IntegrityError as erro:
            if ler_restricao_violada(erro) == RESTRICAO_DE_CNPJ_UNICO:
                raise CnpjJaCadastrado("já existe empresa com este CNPJ") from erro
            raise


def ler_restricao_violada(erro: IntegrityError) -> str | None:
    diagnostico = getattr(erro.orig, "diag", None)
    return getattr(diagnostico, "constraint_name", None)


def converter_em_colunas(empresa: Empresa) -> dict[str, Any]:
    return {
        "razao_social": empresa.razao_social,
        "nome_fantasia": empresa.nome_fantasia,
        "cnpj": empresa.cnpj.valor,
        "situacao": str(empresa.situacao),
    }


def converter_em_empresa(linha: RowMapping) -> Empresa:
    return Empresa(
        id=linha["id"],
        razao_social=linha["razao_social"],
        nome_fantasia=linha["nome_fantasia"],
        cnpj=Cnpj(linha["cnpj"]),
        situacao=SituacaoDaEmpresa(linha["situacao"]),
    )


def criar_empresas(sessao: Session) -> Empresas:
    return EmpresasSqlAlchemy(sessao)
