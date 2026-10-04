from fastapi import FastAPI

from assura.compartilhado.infraestrutura.http import registrar_traducao_de_erros_compartilhados
from assura.configuracao import configuracao
from assura.identidade.infraestrutura.http import registrar_rotas_de_identidade


def criar_aplicacao() -> FastAPI:
    if not configuracao.chave_da_sessao:
        raise RuntimeError("defina ASSURA_CHAVE_DA_SESSAO antes de subir a aplicação")
    aplicacao = FastAPI(title="Assura")
    aplicacao.add_api_route("/saude", verificar_saude, methods=["GET"])
    registrar_rotas_de_identidade(aplicacao)
    registrar_traducao_de_erros_compartilhados(aplicacao)
    return aplicacao


def verificar_saude() -> dict[str, str]:
    return {"situacao": "ok"}


app = criar_aplicacao()
