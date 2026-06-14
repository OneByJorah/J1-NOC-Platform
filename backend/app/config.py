from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    secret_key: str = "change-me"
    database_url: str = "postgresql+psycopg2://jnop:change-me@postgres:5432/jnop"
    redis_url: str = "redis://:change-me@redis:6379/0"
    backend_cors_origins: list[str] = ["http://localhost", "http://127.0.0.1"]
    access_token_expire_minutes: int = 60


def get_settings() -> Settings:
    return Settings()
