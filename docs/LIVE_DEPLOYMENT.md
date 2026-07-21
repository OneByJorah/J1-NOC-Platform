# NexusCore — Live Deployment Guide

## Where live secrets live

Production secrets are stored in `/etc/nexuscore/.env.live` with mode `600`, owned by root. The repo itself never contains live credentials.

## How to update the live server

1. Edit code in the project directory (default `/opt/nexuscore`) as the deploy user.
2. Commit and push to GitHub.
3. Run the deploy script as root:

   ```bash
   sudo /opt/nexuscore/scripts/deploy.sh
   ```

The script:

- Pulls latest code as the configured deploy user.
- Copies `/etc/nexuscore/.env.live` into the project.
- Runs `docker compose up -d --build --remove-orphans`.
- Resets the repo `.env` to `.env.example` so no secrets remain in the working tree.

## How to start/stop the live service via systemd

```bash
sudo cp /opt/nexuscore/systemd/j1-noc-platform.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now j1-noc-platform
```

## Pre-commit hook (secret guard)

Install once per clone:

```bash
cp /opt/nexuscore/.githooks/pre-commit /opt/nexuscore/.git/hooks/pre-commit
chmod +x /opt/nexuscore/.git/hooks/pre-commit
```

This blocks commits that look like they contain passwords, API keys, tokens, or private keys.

## Updating live secrets

Edit `/etc/nexuscore/.env.live` directly on the server. Then re-run the deploy script.

## Environment variables

The following environment variables control the deployment behavior:

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_DIR` | `/opt/nexuscore` | Project installation directory |
| `LIVE_ENV` | `/etc/nexuscore/.env.live` | Path to the live secrets file |
| `DEPLOY_USER` | `appuser` | User that pulls code from Git |
| `NOC_URL` | `http://127.0.0.1:8000` | NOC backend URL used by agents and scripts |

## Important rules

- Never commit `.env`, `.env.live`, `*.pem`, `*.key`, or `*.crt`.
- The repo `.env` should always match `.env.example` (template values only).
- All real credentials must live in `/etc/nexuscore/.env.live`.
