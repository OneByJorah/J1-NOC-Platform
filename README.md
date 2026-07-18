<div align="center">

  <img src="https://raw.githubusercontent.com/OneByJorah/NexusCore/main/docs/logo.png" alt="NexusCore Logo" width="120">

  # 🏢 NexusCore

  **Enterprise NOC Operations Platform**

  DC Replication, NTP, DNS, PBX, Helpdesk, and AI monitoring dashboard for enterprise network operations

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
  [![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
  [![AI-Powered](https://img.shields.io/badge/AI-Powered-9B59B6?style=flat&logo=openai&logoColor=white)](https://openai.com/)

  [Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Services](#-services) • [Contributing](#-contributing)

</div>

---

## 📸 Screenshots

<div align="center">

| NOC Dashboard | Service Monitor | AI Insights |
|---------------|-----------------|-------------|
| ![NOC Dashboard](docs/screenshots/noc-dashboard.png) | ![Service Monitor](docs/screenshots/service-monitor.png) | ![AI Insights](docs/screenshots/ai-insights.png) |

</div>

> 💡 **Tip:** NexusCore provides real-time monitoring of all critical network services with AI-powered anomaly detection

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🖥️ **NOC Dashboard** | Real-time overview of all network operations |
| 🔄 **DC Replication** | Active Directory replication monitoring |
| ⏰ **NTP Monitoring** | Chrony/NTP server health and sync status |
| 🌐 **DNS Management** | BIND/Unbound DNS server monitoring |
| 📞 **PBX Integration** | Asterisk/FreePBX voice system status |
| 🎫 **Helpdesk Integration** | osTicket/OSTiCK ticket tracking |
| 🤖 **AI Monitoring** | Machine learning anomaly detection |
| 📊 **Windows Agent** | Server monitoring agent for Windows |
| 🐳 **Docker Deploy** | One-command deployment |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git
- Network access to monitored services

### Installation

```bash
# Clone the repository
git clone https://github.com/OneByJorah/NexusCore.git
cd NexusCore

# Start with Docker
docker compose up -d
```

### Access the Dashboard

Open **http://localhost:8080** in your browser

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXUS_PORT` | `8080` | Dashboard port |
| `DB_PATH` | `./data/nexus.db` | SQLite database |
| `AI_ENABLED` | `true` | Enable AI monitoring |
| `AD_SERVER` | - | Active Directory server |
| `NTP_SERVERS` | - | Comma-separated NTP servers |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NexusCore                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐      ┌──────────┐      ┌──────────────────────┐  │
│  │ Browser  │ ───▶ │  Nginx   │ ───▶ │    FastAPI Backend    │  │
│  └──────────┘      └──────────┘      └──────────┬───────────┘  │
│                                                  │              │
│  ┌──────────────────────────────────────────────┼───────────┐  │
│  │              Service Connectors              │           │  │
│  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐          │  │
│  │  │ AD  │  │ NTP │  │ DNS │  │ PBX │  │Help │          │  │
│  │  │ Rep │  │Mon  │  │Mon  │  │Mon  │  │desk │          │  │
│  │  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  AI Engine                              │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │   │
│  │  │ Anomaly  │  │Predictive│  │ Alert    │             │   │
│  │  │Detection │  │Analysis  │  │ Routing  │             │   │
│  │  └──────────┘  └──────────┘  └──────────┘             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.10+, FastAPI, SQLAlchemy |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Database** | SQLite / PostgreSQL |
| **AI/ML** | scikit-learn, TensorFlow Lite |
| **Windows Agent** | Python, psutil, httpx |
| **Deployment** | Docker Compose |

---

## 📁 Project Structure

```
NexusCore/
├── backend/                  # FastAPI backend
│   ├── main.py              # Application entry
│   ├── routers/             # API routes
│   │   ├── ad.py            # Active Directory monitoring
│   │   ├── ntp.py           # NTP/Chrony monitoring
│   │   ├── dns.py           # DNS server monitoring
│   │   ├── pbx.py           # PBX monitoring
│   │   └── helpdesk.py      # Helpdesk integration
│   ├── services/            # Business logic
│   │   ├── ai_engine.py     # AI anomaly detection
│   │   └── collectors.py    # Data collection
│   └── models/              # Data models
├── agent/                   # Windows monitoring agent
│   └── windows_agent/       # Agent for Windows servers
├── frontend/                # Dashboard UI
├── docs/                    # Documentation
│   └── screenshots/         # Dashboard screenshots
├── docker-compose.yml       # Docker deployment
└── nginx.conf               # Reverse proxy
```

---

## 🔌 Services

### Active Directory Replication

```bash
# Monitor AD replication status
curl http://localhost:8080/api/ad/replication

# Get replication partners
curl http://localhost:8080/api/ad/partners
```

### NTP Monitoring

```bash
# Check NTP sync status
curl http://localhost:8080/api/ntp/status

# Get NTP servers
curl http://localhost:8080/api/ntp/servers
```

### DNS Monitoring

```bash
# Check DNS server health
curl http://localhost:8080/api/dns/health

# Get DNS zones
curl http://localhost:8080/api/dns/zones
```

### PBX Integration

```bash
# Check PBX status
curl http://localhost:8080/api/pbx/status

# Get active calls
curl http://localhost:8080/api/pbx/calls
```

---

## 🛠️ Development

### Local Development

```bash
# Clone the repository
git clone https://github.com/OneByJorah/NexusCore.git
cd NexusCore

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Windows Agent Setup

```bash
# On Windows server
cd agent/windows_agent
pip install -r requirements.txt
python agent.py --server http://nexuscore-server:8080
```

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔒 Security

For security concerns, please see [SECURITY.md](SECURITY.md).

---

## 💬 Support

- 📧 Email: support@jorah.one
- 🐛 Issues: [GitHub Issues](https://github.com/OneByJorah/NexusCore/issues)
- 📖 Docs: [Documentation](docs/)

---

<div align="center">

  **Built with ❤️ by [Jhonattan L. Jimenez](https://github.com/OneByJorah)**

  [⬆ Back to Top](#-nexuscore)

</div>
