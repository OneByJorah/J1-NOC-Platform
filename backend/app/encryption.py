import base64
import os

from cryptography.fernet import Fernet


def _get_or_create_key() -> bytes:
    """Return the Fernet key from env, or generate and warn if missing."""
    key_env = os.getenv("SETTINGS_ENCRYPTION_KEY")
    if key_env:
        # Accept base64-encoded 32-byte key or raw 32-byte key
        if len(key_env) == 32:
            return base64.urlsafe_b64encode(key_env.encode("utf-8"))
        return key_env.encode("utf-8")
    # Fallback: derive from SECRET_KEY (not ideal but works for single-node deploys)
    secret = os.getenv("SECRET_KEY", "change-me")
    raw = (
        secret.encode("utf-8")[:32].ljust(32, b"\0")
        if isinstance(secret, str)
        else secret[:32].ljust(32, b"\0")
    )
    return base64.urlsafe_b64encode(raw)


def get_fernet() -> Fernet:
    return Fernet(_get_or_create_key())


def encrypt(value: str | None) -> str:
    if value is None:
        return ""
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt(token: str | None) -> str:
    if not token:
        return ""
    try:
        return get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")
    except Exception:
        return ""
