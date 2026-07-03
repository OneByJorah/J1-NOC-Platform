from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from ..database import SessionLocal
from ..models import EncryptedSetting
from ..encryption import encrypt, decrypt
from .auth import get_current_user, require_roles

router = APIRouter()


# Categories for UI grouping
SETTING_CATEGORIES: dict[str, list[str]] = {
    "core": ["SECRET_KEY", "DATABASE_URL", "REDIS_URL"],
    "auth": ["BACKEND_CORS_ORIGINS", "ACCESS_TOKEN_EXPIRE_MINUTES"],
    "monitoring": ["GRAFANA_ADMIN_PASSWORD", "PROMETHEUS_URL"],
    "integrations": [
        "MITEL_SNMP_HOST",
        "MITEL_SNMP_COMMUNITY",
        "OSTICKET_BASE_URL",
        "OSTICKET_API_KEY",
        "WAZUH_API_URL",
        "WAZUH_USERNAME",
        "WAZUH_PASSWORD",
        "WAZUH_VERIFY_SSL",
    ],
    "ai": ["OLLAMA_HOST"],
}


DEFAULT_DESCRIPTIONS: dict[str, str] = {
    "SECRET_KEY": "JWT/session signing key (change to a long random string)",
    "DATABASE_URL": "PostgreSQL connection string",
    "REDIS_URL": "Redis connection string with password",
    "BACKEND_CORS_ORIGINS": "Comma-separated allowed frontend origins",
    "ACCESS_TOKEN_EXPIRE_MINUTES": "Bearer token lifetime in minutes",
    "GRAFANA_ADMIN_PASSWORD": "Grafana admin password",
    "MITEL_SNMP_HOST": "SNMP target host",
    "MITEL_SNMP_COMMUNITY": "SNMP community string",
    "OSTICKET_BASE_URL": "osTicket API base URL",
    "OSTICKER_API_KEY": "osTicket API key",
    "WAZUH_API_URL": "Wazuh API URL",
    "WAZUH_USERNAME": "Wazuh API username",
    "WAZUH_PASSWORD": "Wazuh API password",
    "OLLAMA_HOST": "Ollama host URL",
}


class SettingItem(BaseModel):
    key: str
    value: str
    is_encrypted: bool = True
    category: str | None = None
    description: str | None = None


class SettingsPayload(BaseModel):
    settings: list[SettingItem]


class SettingOut(BaseModel):
    key: str
    value: str
    is_encrypted: bool
    category: str | None
    description: str | None


class SettingsListResponse(BaseModel):
    settings: list[SettingOut]


def _resolve_category(key: str) -> str:
    for category, keys in SETTING_CATEGORIES.items():
        if key in keys:
            return category
    return "other"


def _resolve_description(key: str) -> str:
    return DEFAULT_DESCRIPTIONS.get(key, "")


@router.get("/admin/settings", response_model=SettingsListResponse)
def list_settings(_: Any = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        rows = db.query(EncryptedSetting).order_by(EncryptedSetting.key.asc()).all()
        settings = [
            SettingOut(
                key=row.key,
                value=decrypt(row.value) if row.is_encrypted else row.value,
                is_encrypted=row.is_encrypted,
                category=row.category,
                description=row.description,
            )
            for row in rows
        ]
        # Always include defaults so UI knows what can be configured
        existing_keys = {s.key for s in settings}
        for category, keys in SETTING_CATEGORIES.items():
            for key in keys:
                if key not in existing_keys:
                    settings.append(
                        SettingOut(
                            key=key,
                            value="",
                            is_encrypted=True,
                            category=category,
                            description=_resolve_description(key),
                        )
                    )
        return SettingsListResponse(settings=settings)
    finally:
        db.close()


@router.put("/admin/settings", response_model=SettingsListResponse)
def save_settings(payload: SettingsPayload, _: Any = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        for item in payload.settings:
            category = item.category or _resolve_category(item.key)
            description = item.description or _resolve_description(item.key)
            row = db.query(EncryptedSetting).filter(EncryptedSetting.key == item.key).first()
            new_value = encrypt(item.value) if item.is_encrypted else item.value
            if row:
                row.value = new_value
                row.is_encrypted = item.is_encrypted
                row.category = category
                row.description = description
            else:
                row = EncryptedSetting(
                    key=item.key,
                    value=new_value,
                    is_encrypted=item.is_encrypted,
                    category=category,
                    description=description,
                )
                db.add(row)
        db.commit()
        return list_settings(_)
    finally:
        db.close()


@router.get("/admin/settings/{key}", response_model=SettingOut)
def get_setting(key: str, _: Any = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        row = db.query(EncryptedSetting).filter(EncryptedSetting.key == key).first()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
        return SettingOut(
            key=row.key,
            value=decrypt(row.value) if row.is_encrypted else row.value,
            is_encrypted=row.is_encrypted,
            category=row.category,
            description=row.description,
        )
    finally:
        db.close()


@router.delete("/admin/settings/{key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_setting(key: str, _: Any = Depends(require_roles("admin"))):
    db = SessionLocal()
    try:
        row = db.query(EncryptedSetting).filter(EncryptedSetting.key == key).first()
        if row:
            db.delete(row)
            db.commit()
    finally:
        db.close()


def get_encrypted_setting(key: str, default: str = "") -> str:
    """Used by config loader; reads from DB and decrypts."""
    db = SessionLocal()
    try:
        row = db.query(EncryptedSetting).filter(EncryptedSetting.key == key).first()
        if not row:
            return default
        return decrypt(row.value) if row.is_encrypted else row.value
    finally:
        db.close()
