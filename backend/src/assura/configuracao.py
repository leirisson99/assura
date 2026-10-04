from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ASSURA_")

    url_banco_de_dados: str = "postgresql+psycopg://assura:assura@localhost:5433/assura"
    url_banco_de_dados_de_teste: str = (
        "postgresql+psycopg://assura:assura@localhost:5433/assura_teste"
    )
    # Sem valor padrão de verdade: a aplicação HTTP não sobe com a chave vazia.
    chave_da_sessao: str = ""
    validade_da_sessao_em_horas: int = 8


configuracao = Configuracao()
