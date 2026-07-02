# J1 NOC Operations Platform (JNOP)

**Version:** v5.12  
**Status:** Production Ready  
**Repository:** https://github.com/OneByJorah/J1-NOC-Platform

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Features](#features)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Service Management](#service-management)
- [CI/CD & Deployment](#cicd--deployment)
- [Security](#security)
- [Project Structure](#project-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Overview

The J1 NOC Operations Platform is an enterprise-grade, dark-themed Network Operations Center dashboard built for real-time infrastructure monitoring, alerting, and operations automation. It consolidates monitoring of Domain Controllers, NTP clients, DNS resolution benchmarks, OS images, logs, and helpdesk tickets into a single reactive interface.

The platform is designed to operate in a self-hosted Linux environment with systemd service management. The backend exposes FastAPI endpoints for tab content, users, and RBAC-backed admin management. The frontend is a React + Vite application served behind Nginx and supports dynamic sidebar tabs via backend CRUD.

---

## Architecture

Client → Nginx (`/etc/nginx/sites-enabled/jnop-dashboard.conf`) → FastAPI backend (`/srv/jnop/app`, port `8000`) → monitoring modules (DC, NTP, DNS, Google, Logs, Ollama, PBX, Helpdesk) → notification channels (Email, Telegram, Teams).

Session identity and long-term memory are handled through **Honcho**; short-term context is handled by the platform runtime. Secrets are loaded via `/srv/jnop/config/` with restrictive `0600` permissions (never co-located with data under `/srv/jnop/data`).

---

## Technology Stack

| Layer | Stack |
|-------|-------|
| Runtime | Linux (Ubuntu 22.04+/systemd) |
| Backend | Python / FastAPI / Uvicorn |
| Frontend | React + Vite (Dark Theme, v5.12) |
| Reverse Proxy | Nginx |
| Process Manager | systemd (`jnop-backend.service`) |
| VCS | Git + GitHub (`github.com/OneByJorah/J1-NOC-Platform`) |
| Memory / Context | Honcho (default provider), disabled on this host |
| Notifications | Email, Telegram, Microsoft Teams |
| Admin | Backend CRUD for tabs + users/roles (admin only) |
| Release path | Build frontend and serve dist via Nginx (`/var/www/noc`) |

---

## Features

- **DC Replication**: monitor replication health, latency, LDAP and network status.
- **NTP Monitoring**: client drift tracking, thresholds for WARNING/CRITICAL.
- **DNS Benchmark**: per-DC response time aggregation, CSV export.
- **Log Viewer**: unified event timeline across platform modules.
- **Google Sync**: interface for cloud sync status and health indicators.
- **Ubuntu Server**: host-level metrics and kernel event tracking.
- **Ollama AI**: optional AI operations assistant integration.
- **PBX + Helpdesk**: call-path monitoring; ticket lifecycle tracking.
- **Notification channels**: Email / Telegram / Teams events, with per-channel counters and prefixed styling in logs.
- **Tabs / Admin Console**: backend-managed navigation tabs + admin users/roles pages.
- **Panic Test**: one-click synthetic alert generator.
- **Exportable**: CSV export on supported tabs.

---

## Getting Started

```bash
# 1. Clone the repository
git clone https://github.com/OneByJorah/J1-NOC-Platform.git
cd J1-NOC-Platform

# 2. Backend virtual environment
python3 -m venv /srv/jnop/.venv
source /srv/jnop/.venv/bin/activate
pip install -r requirements.txt

# 3. Environment + config
cp backend/.env.example backend/.env
# Edit backend/.env with your secrets. Keep it out of VCS.
```

---

## Environment Variables

| Variable | Purpose | Notes |
|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter credential (optional) | Used if gateway/auxiliary models require chat completions |
| `DEEPSEEK_API_KEY`, `XAI_API_KEY`, ... | Provider keys | Optional per enabled integration |
| `VITE_API_URL` | Frontend API base | Defaults to `/api` |

Backend `/srv/jnop/config/` uses file-based configuration with `0600` permissions for sensitive values.

---

## Service Management

```bash
# Start the backend service
sudo systemctl start jnop-backend.service
sudo systemctl enable jnop-backend.service

# Tail logs
sudo journalctl -u jnop-backend.service -f

# Build and publish frontend
cd frontend
npm install
npm run build
sudo rsync -a dist/ /var/www/noc/
```

Verify the live frontend size after deploy:

```bash
stat -c "%s %n" /var/www/noc/index.html
# Expect production build output (not a truncated file)
```

Access the dashboard via your configured reverse proxy / hostname.

---

## CI/CD & Deployment

- Trust system-stored credentials for Git operations.
- No token prompts during deploy flows.
- Docker-hosted Crowdsec requires static DNS entries (`8.8.8.8, 1.1.1.1`) if hub resolution fails.
- Frontend build artifacts are served from `/var/www/noc`; backend runs under systemd.

---

## Security

- Secrets are stored in `gitignored` files (`.env`, `/srv/jnop/config/*` with restrictive permissions).
- The deployed dashboard HTML under `/var/www/noc/` is credential-free.
- API mutations for tabs/users require an authenticated admin token.
- `approvals.mode` is set to `manual` by default in Hermes config to prevent unsafe autonomous shell actions; override only when explicitly required.

---

## Project Structure

```
J1-NOC-Platform/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   └── ...
│   │   └── database.py
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── services/
│   │   └── App.tsx
│   └── dist/
│       └── index.html          # Dashboard build output
├── docs/
│   └── screenshots/
├── monitoring/
└── scripts/
    └── sample_seed.sh
```

---

## Screenshots

All screenshots are live captures from the production instance (as of 2026-06-15 v5.12).

### DC Replication
![DC Replication](docs/screenshots/dc-replication.png)

### NTP Monitor
![NTP Monitor](docs/screenshots/ntp-monitor.png)

### DNS Benchmark
![DNS Benchmark](docs/screenshots/dns-benchmark.png)

### Log Viewer
![Log Viewer](docs/screenshots/log-viewer.png)

### Google Sync
![Google Sync](docs/screenshots/google-sync.png)

### Ubuntu Server
![Ubuntu Server](docs/screenshots/ubuntu-server.png)

### Ollama AI
![Ollama AI](docs/screenshots/ollama-ai.png)

### PBX
![PBX](docs/screenshots/pbx.png)

### Helpdesk
![Helpdesk](docs/screenshots/helpdesk.png)

### Admin Tabs
![Admin Tabs](docs/screenshots/admin-tabs.png)

### Admin Users
![Admin Users](docs/screenshots/admin-users.png)

### Admin Roles
![Admin Roles](docs/screenshots/admin-roles.png)

---

## Contributing

1. Create a feature branch off `main`.
2. Ensure no secrets appear in frontend artifacts or README assets.
3. Run backend tests before submitting a PR.
4. Post screenshots for new tabs or UI states to `docs/screenshots/`.

---

## License

MIT

---

## Author

Built by **Jhonattan L. Jimenez**.
