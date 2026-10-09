from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-08-01-preview"

    database_url: str = "postgresql://estate:estate@db:5432/estate"

    app_env: str = "local"
    # Comma-separated list of allowed frontend origins for CORS.
    # In Azure: set this to your Static Web Apps URL, e.g.
    #   https://polite-plant-0d3cf4603-preview.westeurope.7.azurestaticapps.net
    frontend_origin: str = "http://localhost:5173"
    top_k: int = 3

    @property
    def allowed_origins(self) -> list[str]:
        return [o.strip().rstrip("/") for o in self.frontend_origin.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
