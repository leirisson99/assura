from uuid import UUID

from assura.historico import Autor, Detalhes, ObjetoAfetado, RegistrarAcao, TipoDeAcao

TIPO_DE_OBJETO_EMPRESA = "empresa"


def registrar_acao_sobre_empresa(
    registrar_acao: RegistrarAcao,
    *,
    autor: Autor,
    tipo_de_acao: TipoDeAcao,
    empresa_id: UUID,
    detalhes: Detalhes | None = None,
) -> None:
    """Ações sobre uma empresa ficam no histórico da própria empresa."""
    registrar_acao.executar(
        autor=autor,
        tipo_de_acao=tipo_de_acao,
        objeto=ObjetoAfetado(tipo=TIPO_DE_OBJETO_EMPRESA, identificador=str(empresa_id)),
        empresa_id=empresa_id,
        detalhes=detalhes,
    )
