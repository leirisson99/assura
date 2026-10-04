from uuid import UUID

from assura.historico import Autor, Detalhes, ObjetoAfetado, RegistrarAcao, TipoDeAcao
from assura.identidade.dominio.vinculo import Vinculo

TIPO_DE_OBJETO_USUARIO = "usuario"
TIPO_DE_OBJETO_VINCULO = "vinculo"


def registrar_acao_sobre_usuario(
    registrar_acao: RegistrarAcao,
    *,
    autor: Autor,
    tipo_de_acao: TipoDeAcao,
    usuario_id: UUID,
    detalhes: Detalhes | None = None,
) -> None:
    """O usuário é global: ações sobre ele ficam sem empresa (só o administrador do sistema vê)."""
    registrar_acao.executar(
        autor=autor,
        tipo_de_acao=tipo_de_acao,
        objeto=ObjetoAfetado(tipo=TIPO_DE_OBJETO_USUARIO, identificador=str(usuario_id)),
        empresa_id=None,
        detalhes=detalhes,
    )


def registrar_acao_sobre_vinculo(
    registrar_acao: RegistrarAcao, *, autor: Autor, tipo_de_acao: TipoDeAcao, vinculo: Vinculo
) -> None:
    """Ações sobre o vínculo ficam no histórico da empresa do vínculo."""
    registrar_acao.executar(
        autor=autor,
        tipo_de_acao=tipo_de_acao,
        objeto=ObjetoAfetado(tipo=TIPO_DE_OBJETO_VINCULO, identificador=str(vinculo.id)),
        empresa_id=vinculo.empresa_id,
        detalhes={"usuario_id": str(vinculo.usuario_id)},
    )
