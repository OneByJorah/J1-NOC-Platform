from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_parse_none_str=None,
        env_ignore_empty=True,
    )

    secret_key: str = "change-me"
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://jnop:change-me@postgres:5432/jnop",
    )
    redis_url: str = "redis://:change-me@redis:6379/0"
    backend_cors_origins: str = "http://localhost,http://127.0.0.1"
    access_token_expire_minutes: int = 60

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if value is None or value == "":
            return "http://localhost,http://127.0.0.1"
        if isinstance(value, list):
            return ",".join(str(v) for v in value)
        value = str(value).strip()
        if value.startswith("[") and value.endswith("]"):
            try:
                return ",".join(json.loads(value))
            except json.JSONDecodeError:
                pass
        return value

    def get_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    # Wazuh SIEM integration
    wazuh_api_url: str = os.getenv("WAZUH_API_URL", "https://localhost:55000")
    wazuh_username: str = os.getenv("WAZUH_USERNAME", "wazuh")
    wazuh_password: str = os.getenv("WAZUH_PASSWORD", "wazuh")
    wazuh_verify_ssl: str = os.getenv("WAZUH_VERIFY_SSL", "false")

    # Ollama local AI
    ollama_host: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")


def get_settings() -> Settings:
    return Settings()
