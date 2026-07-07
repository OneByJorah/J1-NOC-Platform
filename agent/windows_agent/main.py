"""
J1 NOC Platform - Windows Agent
Collects Windows services, event logs, and custom log files (e.g., Google CloudSync)
Pushes data to NOC backend via HTTP API.
"""
import asyncio
import json
import os
import platform
import socket
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
import psutil
import win32con
import win32evtlog
import win32evtlogutil

# Configuration
NOC_URL = os.getenv("NOC_URL", "http://<noc-tailscale-ip>")
AGENT_TOKEN = os.getenv("AGENT_TOKEN", "change-me")
AGENT_ID_FILE = Path(os.getenv("APPDATA", ".")) / "j1noc" / "agent_id"
CONFIG_FILE = Path(os.getenv("APPDATA", ".")) / "j1noc" / "config.json"

# Collection intervals (seconds)
SERVICE_INTERVAL = 60
EVENT_INTERVAL = 300  # 5 minutes
LOG_INTERVAL = 60
HEARTBEAT_INTERVAL = 30
PUSH_BATCH_SIZE = 100

HEADERS = {
    "Authorization": f"Bearer {AGENT_TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "J1NOC-WindowsAgent/1.0",
}


def get_agent_id() -> str:
    """Get or create persistent agent ID"""
    AGENT_ID_FILE.parent.mkdir(parents=True, exist_ok=True)
    if AGENT_ID_FILE.exists():
        return AGENT_ID_FILE.read_text().strip()
    agent_id = str(uuid.uuid4())
    AGENT_ID_FILE.write_text(agent_id)
    return agent_id


def load_config() -> dict[str, Any]:
    """Load agent configuration"""
    default = {
        "event_channels": ["System", "Application"],
        "event_levels": ["ERROR", "WARNING", "CRITICAL"],
        "event_lookback_hours": 1,
        "log_sources": [
            {
                "name": "googledrive",
                "paths": [
                    r"C:\Program Files\Google\Drive File Stream\logs\*.log",
                    r"C:\Users\*\AppData\Local\Google\DriveFS\logs\*.log",
                ],
                "patterns": [
                    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d+Z?)\s+(?P<level>\w+)\s+(?P<message>.+)",
                ],
            },
        ],
        "tags": [],
    }
    if CONFIG_FILE.exists():
        try:
            user_config = json.loads(CONFIG_FILE.read_text())
            default.update(user_config)
        except Exception:
            pass
    return default


def save_config(config: dict[str, Any]):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_hostname() -> str:
    return socket.gethostname()


def get_ip_address() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_os_version() -> str:
    return f"{platform.system()} {platform.release()} {platform.version()}"


# ===================== COLLECTORS =====================

async def collect_services() -> list[dict[str, Any]]:
    """Collect Windows services"""
    services = []
    try:
        for svc in psutil.win_service_iter():
            try:
                info = svc.as_dict()
                # Get additional info via psutil.Process if running
                cpu = None
                mem = None
                if info.get("pid"):
                    try:
                        p = psutil.Process(info["pid"])
                        cpu = p.cpu_percent(interval=0.1)
                        mem = p.memory_info().rss // (1024 * 1024)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass

                services.append({
                    "service_name": info.get("name", ""),
                    "display_name": info.get("display_name", ""),
                    "status": info.get("status", "unknown"),
                    "start_type": info.get("start_type", "unknown"),
                    "pid": info.get("pid"),
                    "cpu_percent": cpu,
                    "memory_mb": mem,
                    "description": info.get("description", ""),
                })
            except Exception:
                continue
    except Exception as e:
        print(f"[WARN] Service collection failed: {e}")
    return services


async def collect_events(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect Windows Event Log entries"""
    events = []
    channels = config.get("event_channels", ["System", "Application"])
    levels = set(config.get("event_levels", ["ERROR", "WARNING", "CRITICAL"]))
    lookback_hours = config.get("event_lookback_hours", 1)
    cutoff = datetime.now() - timedelta(hours=lookback_hours)

    # Level mapping: win32evtlog constants -> our strings
    LEVEL_MAP = {
        win32con.EVENTLOG_ERROR_TYPE: "ERROR",
        win32con.EVENTLOG_WARNING_TYPE: "WARNING",
        win32con.EVENTLOG_INFORMATION_TYPE: "INFORMATION",
        win32con.EVENTLOG_AUDIT_SUCCESS: "SUCCESS",
        win32con.EVENTLOG_AUDIT_FAILURE: "FAILURE",
    }

    for channel in channels:
        try:
            handle = win32evtlog.OpenEventLog(None, channel)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

            while True:
                records = win32evtlog.ReadEventLog(handle, flags, 0)
                if not records:
                    break

                for record in records:
                    # Filter by time
                    record_time = record.TimeGenerated
                    if record_time < cutoff:
                        break

                    # Map level
                    level = LEVEL_MAP.get(record.EventType, "INFORMATION")
                    if level not in levels:
                        continue

                    # Get message
                    try:
                        message = win32evtlogutil.SafeFormatMessage(record, channel)
                    except Exception:
                        message = str(record.StringInserts) if record.StringInserts else ""

                    events.append({
                        "event_id": record.EventID & 0xFFFF,
                        "level": level,
                        "source": record.SourceName,
                        "channel": channel,
                        "message": message[:4000],  # Limit size
                        "computer": record.ComputerName,
                        "user_sid": str(record.Sid) if record.Sid else None,
                        "category": str(record.EventCategory) if record.EventCategory else None,
                        "recorded_at": record_time.isoformat(),
                    })

                # Limit per channel
                if len(events) >= PUSH_BATCH_SIZE:
                    break

            win32evtlog.CloseEventLog(handle)
        except Exception as e:
            print(f"[WARN] Event collection failed for {channel}: {e}")

    return events[:PUSH_BATCH_SIZE]


def parse_log_line(line: str, patterns: list[str]) -> dict[str, Any] | None:
    """Parse a log line using regex patterns"""
    import re
    for pattern in patterns:
        try:
            match = re.match(pattern, line)
            if match:
                groups = match.groupdict()
                # Parse timestamp
                ts_str = groups.get("timestamp", "")
                timestamp = datetime.now()
                for fmt in [
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                    "%Y-%m-%dT%H:%M:%SZ",
                    "%Y-%m-%d %H:%M:%S,%f",
                    "%Y-%m-%d %H:%M:%S",
                    "%m/%d/%Y %H:%M:%S",
                ]:
                    try:
                        timestamp = datetime.strptime(ts_str, fmt)
                        break
                    except ValueError:
                        continue

                return {
                    "timestamp": timestamp.isoformat(),
                    "level": groups.get("level", "INFO").upper(),
                    "message": groups.get("message", line)[:4000],
                    "extra": {k: v for k, v in groups.items() if k not in ("timestamp", "level", "message")},
                }
        except Exception:
            continue
    return None


async def collect_logs(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Collect custom log files (Google CloudSync, etc.)"""
    logs = []
    log_sources = config.get("log_sources", [])

    for source in log_sources:
        source_name = source.get("name", "unknown")
        paths = source.get("paths", [])
        patterns = source.get("patterns", [r"(?P<timestamp>.+?)\s+(?P<level>\w+)\s+(?P<message>.+)"])

        for path_pattern in paths:
            # Expand wildcards and user paths
            import glob
            expanded_paths = glob.glob(path_pattern)
            for file_path in expanded_paths:
                try:
                    # Read last 1000 lines
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()[-1000:]

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        parsed = parse_log_line(line, patterns)
                        if parsed:
                            logs.append({
                                "log_source": source_name,
                                "file_path": file_path,
                                **parsed,
                            })
                except Exception as e:
                    print(f"[WARN] Log collection failed for {file_path}: {e}")

    return logs[:PUSH_BATCH_SIZE]


# ===================== NETWORK =====================

async def push_data(payload: dict[str, Any]) -> bool:
    """Push data to NOC backend"""
    url = f"{NOC_URL}/api/agent/push"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json=payload, headers=HEADERS)
            if resp.status_code == 200:
                return True
            else:
                print(f"[ERROR] Push failed: {resp.status_code} - {resp.text}")
                return False
    except Exception as e:
        print(f"[ERROR] Push exception: {e}")
        return False


async def send_heartbeat(agent_id: str, status: str = "online", config: dict = None):
    """Send heartbeat to NOC"""
    url = f"{NOC_URL}/api/agent/heartbeat"
    payload = {"agent_id": agent_id, "status": status, "config": config or {}}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(url, json=payload, headers=HEADERS)
    except Exception:
        pass


# ===================== MAIN LOOP =====================

async def register_agent(agent_id: str, config: dict[str, Any]) -> bool:
    """Register agent with NOC"""
    url = f"{NOC_URL}/api/agent/register"
    payload = {
        "agent_id": agent_id,
        "hostname": get_hostname(),
        "ip_address": get_ip_address(),
        "os_version": get_os_version(),
        "agent_version": "1.0.0",
        "tags": config.get("tags", []),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload, headers=HEADERS)
            return resp.status_code == 200
    except Exception as e:
        print(f"[ERROR] Registration failed: {e}")
        return False


async def main_loop():
    print(f"[INFO] Starting J1 NOC Windows Agent")
    print(f"[INFO] NOC URL: {NOC_URL}")
    print(f"[INFO] Hostname: {get_hostname()}")

    agent_id = get_agent_id()
    print(f"[INFO] Agent ID: {agent_id}")

    config = load_config()
    print(f"[INFO] Config loaded: {len(config.get('event_channels', []))} event channels, {len(config.get('log_sources', []))} log sources")

    # Register
    if not await register_agent(agent_id, config):
        print("[ERROR] Failed to register agent, retrying in 30s...")
        await asyncio.sleep(30)
        if not await register_agent(agent_id, config):
            print("[FATAL] Registration failed permanently")
            return

    print("[INFO] Agent registered successfully")

    # Timers
    last_service = 0
    last_event = 0
    last_log = 0
    last_heartbeat = 0

    while True:
        now = time.time()

        # Heartbeat
        if now - last_heartbeat >= HEARTBEAT_INTERVAL:
            await send_heartbeat(agent_id, "online", config)
            last_heartbeat = now

        # Services
        if now - last_service >= SERVICE_INTERVAL:
            print("[INFO] Collecting services...")
            services = await collect_services()
            payload = {"agent": {"agent_id": agent_id}, "services": services}
            await push_data(payload)
            print(f"[INFO] Pushed {len(services)} services")
            last_service = now

        # Events
        if now - last_event >= EVENT_INTERVAL:
            print("[INFO] Collecting events...")
            events = await collect_events(config)
            payload = {"agent": {"agent_id": agent_id}, "events": events}
            await push_data(payload)
            print(f"[INFO] Pushed {len(events)} events")
            last_event = now

        # Logs
        if now - last_log >= LOG_INTERVAL:
            print("[INFO] Collecting logs...")
            logs = await collect_logs(config)
            payload = {"agent": {"agent_id": agent_id}, "logs": logs}
            await push_data(payload)
            print(f"[INFO] Pushed {len(logs)} log entries")
            last_log = now

        await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("\n[INFO] Agent stopped by user")
    except Exception as e:
        print(f"[FATAL] Agent crashed: {e}")
        sys.exit(1)