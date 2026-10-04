from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracao(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="ASSURA_")

    url_banco_de_dados: str = "postgresql+psycopg://assura:assura@localhost:5433/assura"


configuracao = Configuracao()
