<div align="center">
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">
  <img src="https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white">
</div>

<br>

<div align="center">
  <h1>🏢 J1 NOC Operations Platform (JNOP)</h1>
  <p><strong>Enterprise NOC Dashboard — v11.0 Production Ready</strong></p>
  <p>Real-time infrastructure monitoring, alerting, and operations automation</p>
  <p>
    <a href="#-features">Features</a> •
    <a href="#-quick-start">Quick Start</a> •
    <a href="#-architecture">Architecture</a> •
    <a href="#-services">Services</a>
  </p>
</div>

---

## ✨ Features

- **Real-Time Monitoring** — DC, NTP, DNS, OS images, logs, helpdesk, SIEM
- **RBAC Administration** — Role-based access control
- **AI Integration** — Ollama-powered AI assistant
- **Wazuh SIEM** — Security monitoring and event correlation
- **React + Vite Frontend** — Modern reactive dark-themed UI
- **FastAPI Backend** — High-performance async API
- **Docker Stack** — Complete containerized deployment
- **Auto-Install** — One-command setup for Ubuntu/Debian

## 🚀 Quick Start

```bash
git clone https://github.com/OneByJorah/J1-NOC-Platform.git
cd J1-NOC-Platform
sudo ./setup.sh
```

## 🏗️ Architecture

```
J1-NOC-Platform/
├── frontend/                  # React + Vite SPA
├── backend/                   # FastAPI backend
├── admin-service/             # Admin & RBAC service
├── agent/                     # Monitoring agents
├── database/                  # Database migrations
├── monitoring/                # Wazuh SIEM integration
├── nginx/                     # Reverse proxy config
├── systemd/                   # systemd service files
├── docker-compose.yml         # Main deployment
├── setup.sh                   # Auto-install script
└── docs/                      # Documentation
```

## 🔧 Services Monitored

| Service | Type | Description |
|---------|------|-------------|
| Domain Controllers | AD | Replication & health |
| NTP Clients | Time | Clock sync status |
| DNS Performance | Network | Query latency |
| OS Images | Deployment | Image management |
| Logs | System | Centralized logging |
| Helpdesk | Support | Ticket monitoring |
| Wazuh SIEM | Security | Event correlation |
| Ollama AI | LLM | AI assistant |

## 📄 License

MIT © Jhonattan L. Jimenez

---

<div align="center">
  <p>🏢 Enterprise NOC, self-hosted</p>
  <p><a href="https://github.com/OneByJorah">@OneByJorah</a></p>
</div>
