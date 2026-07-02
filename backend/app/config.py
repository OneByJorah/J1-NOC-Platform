from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "change-me"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://jnop:change-me@postgres:5432/jnop",
    )
    redis_url: str = "redis://:change-me@redis:6379/0"
    backend_cors_origins: list[str] = ["http://localhost", "http://127.0.0.1"]
    access_token_expire_minutes: int = 60

    # Wazuh SIEM integration
    wazuh_api_url: str = os.getenv("WAZUH_API_URL", "https://localhost:55000")
    wazuh_username: str = os.getenv("WAZUH_USERNAME", "wazuh")
    wazuh_password: str = os.getenv("WAZUH_PASSWORD", "wazuh")
    wazuh_verify_ssl: str = os.getenv("WAZUH_VERIFY_SSL", "false")

    # Ollama local AI
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def get_settings() -> Settings:
    return Settings()
