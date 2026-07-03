from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
import json
import os


# Runtime-cached DB-backed overrides (populated lazily by config loader)
_db_overrides: dict[str, str] = {}


def _env_or_db(key: str, default: str = "") -> str:
    """Return env var if set and non-empty, otherwise check DB overrides."""
    env_value = os.getenv(key)
    if env_value:
        return env_value
    return _db_overrides.get(key, default)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_parse_none_str=None,
        env_ignore_empty=True,
    )

    secret_key: str = "change-me"
    database_url: str = _env_or_db(
        "DATABASE_URL",
        "postgresql+psycopg2://jnop:change-me@postgres:5432/jnop",
    )
    redis_url: str = _env_or_db("REDIS_URL", "redis://:change-me@redis:6379/0")
    backend_cors_origins: str = _env_or_db(
        "BACKEND_CORS_ORIGINS",
        "http://localhost,http://127.0.0.1",
    )
    access_token_expire_minutes: int = int(_env_or_db("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

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
    wazuh_api_url: str = _env_or_db("WAZUH_API_URL", "https://localhost:55000")
    wazuh_username: str = _env_or_db("WAZUH_USERNAME", "wazuh")
    wazuh_password: str = _env_or_db("WAZUH_PASSWORD", "wazuh")
    wazuh_verify_ssl: str = _env_or_db("WAZUH_VERIFY_SSL", "false")

    # Ollama local AI
    ollama_host: str = _env_or_db("OLLAMA_HOST", "http://localhost:11434")

    # SNMP / osTicket
    mitel_snmp_host: str = _env_or_db("MITEL_SNMP_HOST", "localhost")
    mitel_snmp_community: str = _env_or_db("MITEL_SNMP_COMMUNITY", "public")
    osticket_base_url: str = _env_or_db("OSTICKET_BASE_URL", "")
    osticket_api_key: str = _env_or_db("OSTICKET_API_KEY", "")
    grafana_admin_password: str = _env_or_db("GRAFANA_ADMIN_PASSWORD", "change-me")


def refresh_db_settings():
    """Load all encrypted DB settings into memory overrides."""
    global _db_overrides
    try:
        from .database import SessionLocal
        from .models import EncryptedSetting
        from .encryption import decrypt

        db = SessionLocal()
        try:
            rows = db.query(EncryptedSetting).all()
            _db_overrides = {
                row.key: (decrypt(row.value) if row.is_encrypted else row.value)
                for row in rows
            }
        finally:
            db.close()
    except Exception:
        # DB may not be available during import/startup bootstrap
        _db_overrides = {}


def get_settings() -> Settings:
    refresh_db_settings()
    return Settings()


def get_db_setting(key: str, default: str = "") -> str:
    """Direct DB read for a single setting; used by routers after startup."""
    from .database import SessionLocal
    from .models import EncryptedSetting
    from .encryption import decrypt

    db = SessionLocal()
    try:
        row = db.query(EncryptedSetting).filter(EncryptedSetting.key == key).first()
        if not row:
            return default
        return decrypt(row.value) if row.is_encrypted else row.value
    finally:
        db.close()
