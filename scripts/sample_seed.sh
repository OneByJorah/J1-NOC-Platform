#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found" >&2
  exit 1
fi

if ! python3 - <<'PY' >/dev/null 2>&1
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

try:
    from backend.app.database import SessionLocal, Base
    from backend.app.models import Tab, User, Role
except Exception as exc:
    raise SystemExit(exc)

from backend.app.config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, future=True)
local_engine = create_engine(settings.database_url.replace("postgresql+psycopg2", "sqlite+pysqlite"), future=True)

Base.metadata.create_all(bind=local_engine)
PY
then
  echo "Python backend import failed. Run from backend/.venv with requirements installed." >&2
  exit 1
fi

python3 - <<'PY'
from sqlalchemy.orm import Session

try:
    from backend.app.database import SessionLocal
    from backend.app.models import Tab
    from backend.app.config import get_settings
except Exception as exc:
    raise SystemExit(exc)
from sqlalchemy import inspect

settings = get_settings()
session: Session = SessionLocal()
try:
    inspector = inspect(session.bind)
    if not inspector.has_table("tabs"):
        Base.metadata.create_all(bind=session.bind)
    existing = {row.path for row in session.query(Tab.path).all()}
    defaults = [
        {"path": "/", "label": "Home", "sort_order": 1, "is_visible": True, "icon": "home"},
        {"path": "/ldap", "label": "LDAP", "sort_order": 2, "is_visible": True, "icon": "people"},
        {"path": "/snmp", "label": "SNMP / PBX", "sort_order": 3, "is_visible": True, "icon": "network"},
        {"path": "/tickets", "label": "Helpdesk", "sort_order": 4, "is_visible": True, "icon": "ticket"},
        {"path": "/dns", "label": "DNS", "sort_order": 5, "is_visible": True, "icon": "dns"},
        {"path": "/chrony", "label": "Chrony", "sort_order": 6, "is_visible": True, "icon": "schedule"},
        {"path": "/wazuh", "label": "Wazuh SIEM", "sort_order": 7, "is_visible": True, "icon": "security"},
        {"path": "/admin", "label": "Admin", "sort_order": 8, "is_visible": True, "icon": "settings"},
        {"path": "/ai", "label": "AI", "sort_order": 9, "is_visible": True, "icon": "psychology"},
    ]
    created = 0
    for item in defaults:
        if item["path"] in existing:
            continue
        session.add(Tab(**item))
        created += 1
    session.commit()
    print(f"Tabs seeded: {created}")
finally:
    session.close()
PY
