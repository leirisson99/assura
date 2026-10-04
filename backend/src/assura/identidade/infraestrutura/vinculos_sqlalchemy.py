from uuid import UUID

from sqlalchemy import RowMapping, exists, func, insert, select, update
from sqlalchemy.orm import Session

from assura.compartilhado.dominio.pagina import Pagina
from assura.compartilhado.infraestrutura.banco import executar_traduzindo_restricoes
from assura.identidade.aplicacao.portas import UsuarioDaEmpresa, Vinculos
from assura.identidade.dominio.erros import VinculoJaExiste, VinculoNaoEncontrado
from assura.identidade.dominio.vinculo import SituacaoDoVinculo, Vinculo
from assura.identidade.infraestrutura.tabela import tabela_usuario, tabela_vinculo
from assura.identidade.infraestrutura.usuarios_sqlalchemy import converter_em_usuario

colunas = tabela_vinculo.c
RESTRICAO_DE_VINCULO_UNICO = "uq_vinculo_usuario_empresa"


class VinculosSqlAlchemy:
    def __init__(self, sessao: Session) -> None:
        self._sessao = sessao

    def adicionar(self, vinculo: Vinculo) -> None:
        executar_traduzindo_restricoes(
            self._sessao,
            insert(tabela_vinculo).values(
                id=vinculo.id,
                usuario_id=vinculo.usuario_id,
                empresa_id=vinculo.empresa_id,
                situacao=str(vinculo.situacao),
            ),
            {
                RESTRICAO_DE_VINCULO_UNICO: lambda: VinculoJaExiste(
                    "o usuário já tem vínculo com esta empresa"
                )
            },
        )

    def atualizar(self, vinculo: Vinculo) -> None:
        self._sessao.execute(
            update(tabela_vinculo)
            .where(colunas.id == vinculo.id)
            .values(situacao=str(vinculo.situacao))
        )

    def obter(self, vinculo_id: UUID) -> Vinculo:
        linha = (
            self._sessao.execute(select(tabela_vinculo).where(colunas.id == vinculo_id))
            .mappings()
            .one_or_none()
        )
        if linha is None:
            raise VinculoNaoEncontrado(f"vínculo {vinculo_id} não encontrado")
        return converter_em_vinculo(linha)

    def existe(self, usuario_id: UUID, empresa_id: UUID) -> bool:
        condicao = (colunas.usuario_id == usuario_id) & (colunas.empresa_id == empresa_id)
        return bool(self._sessao.scalar(select(exists().where(condicao))))

    def listar_da_empresa(
        self, empresa_id: UUID, situacao: SituacaoDoVinculo | None, pagina: Pagina
    ) -> list[UsuarioDaEmpresa]:
        consulta = (
            select(
                tabela_usuario,
                colunas.id.label("vinculo_id"),
                colunas.empresa_id,
                colunas.situacao.label("vinculo_situacao"),
            )
            .join(tabela_vinculo, colunas.usuario_id == tabela_usuario.c.id)
            .where(colunas.empresa_id == empresa_id)
        )
        if situacao is not None:
            consulta = consulta.where(colunas.situacao == str(situacao))
        consulta = (
            consulta.order_by(func.lower(tabela_usuario.c.nome), tabela_usuario.c.id)
            .limit(pagina.tamanho)
            .offset(pagina.deslocamento)
        )
        return [
            UsuarioDaEmpresa(
                usuario=converter_em_usuario(linha),
                vinculo=Vinculo(
                    id=linha["vinculo_id"],
                    usuario_id=linha["id"],
                    empresa_id=linha["empresa_id"],
                    situacao=SituacaoDoVinculo(linha["vinculo_situacao"]),
                ),
            )
            for linha in self._sessao.execute(consulta).mappings()
        ]


def converter_em_vinculo(linha: RowMapping) -> Vinculo:
    return Vinculo(
        id=linha["id"],
        usuario_id=linha["usuario_id"],
        empresa_id=linha["empresa_id"],
        situacao=SituacaoDoVinculo(linha["situacao"]),
    )


def criar_vinculos(sessao: Session) -> Vinculos:
    return VinculosSqlAlchemy(sessao)
