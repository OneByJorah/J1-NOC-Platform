from fastapi import APIRouter
from fastapi.responses import JSONResponse
import json
import pathlib

router = APIRouter()
BASE = pathlib.Path('/srv/jnop/data')


def _load_json(filename: str) -> dict:
    """Load JSON data from data directory, return empty dict on failure."""
    p = BASE / filename
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


def _count_tickets() -> int:
    """Return open ticket count from helpdesk data."""
    try:
        tickets = _load_json('helpdesk_tickets.json')
        if isinstance(tickets, list):
            return len([t for t in tickets if t.get('status', '').lower() in ('open', 'in progress', 'new')])
    except Exception:
        pass
    return 0


@router.get("/dashboard/overview")
def dashboard_overview():
    """Return platform overview metrics for the dashboard home page."""
    dc_status = _load_json('dc_status.json')
    ntp_status = _load_json('ntp_status.json')

    # Count devices from DC status
    dcs = dc_status.get('DCs', dc_status.get('dc_status', []))
    total_devices = len(dcs) if isinstance(dcs, list) else 0
    online_devices = len([d for d in dcs if isinstance(d, dict) and d.get('status', '').lower() == 'ok'])

    # Count NTP clients and derive alerts
    clients = ntp_status.get('Clients', ntp_status.get('clients', []))
    total_clients = len(clients) if isinstance(clients, list) else 0
    online_ntp = len([c for c in clients if isinstance(c, dict) and c.get('status', '').lower() == 'ok'])

    # Count alerts: NTP warnings + offline DCs
    active_alerts = 0
    critical_alerts = 0
    for c in clients:
        if isinstance(c, dict):
            status = c.get('status', '').lower()
            if status == 'critical':
                critical_alerts += 1
            elif status in ('warn', 'warning'):
                active_alerts += 1
    active_alerts += total_devices - online_devices  # offline DCs

    open_tickets = _count_tickets()

    return JSONResponse({
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": total_devices - online_devices,
        "active_alerts": active_alerts,
        "critical_alerts": critical_alerts,
        "open_tickets": open_tickets,
    })
