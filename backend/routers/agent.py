from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func as sqlfunc

from ..database import SessionLocal, engine
from ..models import WindowsAgent, WindowsService, WindowsEvent, WindowsLogEntry

router = APIRouter(prefix="/agent", tags=["agent"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===================== PYDANTIC SCHEMAS =====================

class AgentRegister(BaseModel):
    agent_id: str
    hostname: str
    ip_address: Optional[str] = None
    os_version: Optional[str] = None
    agent_version: str = "1.0.0"
    tags: List[str] = []


class AgentHeartbeat(BaseModel):
    agent_id: str
    status: str = "online"
    config: dict = {}


class ServiceData(BaseModel):
    service_name: str
    display_name: Optional[str] = None
    status: str
    start_type: Optional[str] = None
    pid: Optional[int] = None
    cpu_percent: Optional[float] = None
    memory_mb: Optional[int] = None
    description: Optional[str] = None


class EventData(BaseModel):
    event_id: int
    level: str
    source: str
    channel: str
    message: str
    computer: Optional[str] = None
    user_sid: Optional[str] = None
    category: Optional[str] = None
    raw_xml: Optional[str] = None
    recorded_at: datetime


class LogEntryData(BaseModel):
    log_source: str
    file_path: Optional[str] = None
    level: Optional[str] = None
    message: str
    timestamp: datetime
    extra: dict = {}


class AgentPayload(BaseModel):
    """Combined payload from Python agent"""
    agent: AgentRegister
    services: List[ServiceData] = []
    events: List[EventData] = []
    logs: List[LogEntryData] = []


class TelegrafMetric(BaseModel):
    """Telegraf HTTP JSON format"""
    name: str
    tags: dict = {}
    fields: dict
    timestamp: Optional[int] = None  # Unix nanoseconds


# ===================== HELPER FUNCTIONS =====================

def get_or_create_agent(db: Session, agent_data: AgentRegister) -> WindowsAgent:
    agent = db.query(WindowsAgent).filter(WindowsAgent.agent_id == agent_data.agent_id).first()
    if not agent:
        agent = WindowsAgent(
            agent_id=agent_data.agent_id,
            hostname=agent_data.hostname,
            ip_address=agent_data.ip_address,
            os_version=agent_data.os_version,
            agent_version=agent_data.agent_version,
            tags=agent_data.tags,
            status="online",
            last_seen=datetime.utcnow(),
        )
        db.add(agent)
    else:
        agent.hostname = agent_data.hostname
        agent.ip_address = agent_data.ip_address
        agent.os_version = agent_data.os_version
        agent.agent_version = agent_data.agent_version
        agent.tags = agent_data.tags
        agent.status = "online"
        agent.last_seen = datetime.utcnow()
    db.flush()
    return agent


def update_agent_heartbeat(db: Session, agent_id: str, status: str, config: dict):
    agent = db.query(WindowsAgent).filter(WindowsAgent.agent_id == agent_id).first()
    if agent:
        agent.status = status
        agent.last_seen = datetime.utcnow()
        if config:
            agent.config = config


def ingest_services(db: Session, agent: WindowsAgent, services: List[ServiceData]):
    """Store service snapshots"""
    for svc in services:
        # Skip if we want to limit storage - keep last N per service
        snapshot = WindowsService(
            agent_id=agent.id,
            service_name=svc.service_name,
            display_name=svc.display_name,
            status=svc.status,
            start_type=svc.start_type,
            pid=svc.pid,
            cpu_percent=int(svc.cpu_percent * 100) if svc.cpu_percent else None,
            memory_mb=svc.memory_mb,
            description=svc.description,
            collected_at=datetime.utcnow(),
        )
        db.add(snapshot)


def ingest_events(db: Session, agent: WindowsAgent, events: List[EventData]):
    """Store event log entries"""
    for evt in events:
        event = WindowsEvent(
            agent_id=agent.id,
            event_id=evt.event_id,
            level=evt.level.upper(),
            source=evt.source,
            channel=evt.channel,
            message=evt.message,
            computer=evt.computer,
            user_sid=evt.user_sid,
            category=evt.category,
            raw_xml=evt.raw_xml,
            recorded_at=evt.recorded_at,
            collected_at=datetime.utcnow(),
        )
        db.add(event)


def ingest_logs(db: Session, agent: WindowsAgent, logs: List[LogEntryData]):
    """Store log file entries"""
    for log in logs:
        entry = WindowsLogEntry(
            agent_id=agent.id,
            log_source=log.log_source,
            file_path=log.file_path,
            level=log.level.upper() if log.level else None,
            message=log.message,
            timestamp=log.timestamp,
            collected_at=datetime.utcnow(),
            extra=log.extra,
        )
        db.add(entry)


# ===================== PYTHON AGENT ENDPOINTS =====================

@router.post("/register")
async def register_agent(payload: AgentRegister, db: Session = Depends(get_db)):
    """Register a new Windows agent"""
    agent = get_or_create_agent(db, payload)
    db.commit()
    return {"success": True, "agent_id": agent.agent_id, "db_id": agent.id}


@router.post("/push")
async def push_agent_data(payload: AgentPayload, db: Session = Depends(get_db)):
    """
    Main endpoint for Python agent to push batch data.
    Expects combined payload with agent info + services + events + logs.
    """
    agent = get_or_create_agent(db, payload.agent)

    if payload.services:
        ingest_services(db, agent, payload.services)

    if payload.events:
        ingest_events(db, agent, payload.events)

    if payload.logs:
        ingest_logs(db, agent, payload.logs)

    agent.last_seen = datetime.utcnow()
    agent.status = "online"

    db.commit()
    return {
        "success": True,
        "services": len(payload.services),
        "events": len(payload.events),
        "logs": len(payload.logs),
    }


@router.post("/heartbeat")
async def agent_heartbeat(payload: AgentHeartbeat, db: Session = Depends(get_db)):
    """Simple heartbeat from agent"""
    update_agent_heartbeat(db, payload.agent_id, payload.status, payload.config)
    db.commit()
    return {"success": True}


# ===================== TELEGRAF ENDPOINT =====================

@router.post("/telegraf")
async def ingest_telegraf(
    request: Request,
    db: Session = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """
    Telegraf HTTP output endpoint.
    Expects JSON array of metrics in Telegraf format:
    [
      {"name": "win_cpu", "tags": {"host": "SERVER01"}, "fields": {"usage": 15.5}, "timestamp": 1234567890000000000},
      ...
    ]
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    if not isinstance(body, list):
        body = [body]

    # Verify token if configured (optional)
    # token = authorization.replace("Bearer ", "") if authorization else None

    agents_seen = set()
    metrics_count = 0

    for metric in body:
        if not isinstance(metric, dict):
            continue

        name = metric.get("name", "")
        tags = metric.get("tags", {})
        fields = metric.get("fields", {})
        ts_ns = metric.get("timestamp")

        hostname = tags.get("host") or tags.get("hostname") or "unknown"
        metrics_count += 1

        # Find or create agent by hostname
        agent = db.query(WindowsAgent).filter(WindowsAgent.hostname == hostname).first()
        if not agent:
            agent = WindowsAgent(
                agent_id=f"telegraf-{hostname}",
                hostname=hostname,
                ip_address=tags.get("ip"),
                os_version=tags.get("os"),
                agent_version="telegraf",
                tags=["telegraf"],
                status="online",
                last_seen=datetime.utcnow(),
            )
            db.add(agent)
            db.flush()

        agents_seen.add(agent.id)

        # Convert timestamp
        recorded_at = datetime.utcnow()
        if ts_ns:
            try:
                recorded_at = datetime.fromtimestamp(ts_ns / 1_000_000_000)
            except Exception:
                pass

        # Store based on metric name
        if name.startswith("win_service") or name == "service":
            svc = WindowsService(
                agent_id=agent.id,
                service_name=tags.get("name", "unknown"),
                display_name=tags.get("display_name"),
                status=fields.get("status", "unknown"),
                start_type=tags.get("start_type"),
                pid=fields.get("pid"),
                cpu_percent=int(fields.get("cpu_percent", 0) * 100) if fields.get("cpu_percent") else None,
                memory_mb=fields.get("memory_mb"),
                description=tags.get("description"),
                collected_at=recorded_at,
            )
            db.add(svc)

        elif name.startswith("win_event") or name == "event":
            evt = WindowsEvent(
                agent_id=agent.id,
                event_id=fields.get("event_id", 0),
                level=tags.get("level", "INFORMATION").upper(),
                source=tags.get("source", "Telegraf"),
                channel=tags.get("channel", "System"),
                message=fields.get("message", ""),
                computer=tags.get("computer"),
                recorded_at=recorded_at,
            )
            db.add(evt)

        elif name.startswith("win_log") or name == "log":
            log = WindowsLogEntry(
                agent_id=agent.id,
                log_source=tags.get("source", "telegraf"),
                file_path=tags.get("file"),
                level=tags.get("level"),
                message=fields.get("message", ""),
                timestamp=recorded_at,
                extra=fields,
            )
            db.add(log)

    # Update last_seen for all agents that sent data
    for agent_id in agents_seen:
        agent = db.query(WindowsAgent).filter(WindowsAgent.id == agent_id).first()
        if agent:
            agent.last_seen = datetime.utcnow()
            agent.status = "online"

    db.commit()
    return {"success": True, "metrics_processed": metrics_count, "agents": len(agents_seen)}


# ===================== QUERY ENDPOINTS (for dashboard) =====================

@router.get("/agents")
async def list_agents(db: Session = Depends(get_db)):
    agents = db.query(WindowsAgent).order_by(WindowsAgent.last_seen.desc().nullslast()).all()
    return [
        {
            "id": a.id,
            "agent_id": a.agent_id,
            "hostname": a.hostname,
            "ip_address": a.ip_address,
            "os_version": a.os_version,
            "agent_version": a.agent_version,
            "status": a.status,
            "last_seen": a.last_seen.isoformat() if a.last_seen else None,
            "tags": a.tags,
        }
        for a in agents
    ]


@router.get("/agents/{agent_id}/services")
async def get_agent_services(agent_id: int, limit: int = 100, db: Session = Depends(get_db)):
    services = (
        db.query(WindowsService)
        .filter(WindowsService.agent_id == agent_id)
        .order_by(WindowsService.collected_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "service_name": s.service_name,
            "display_name": s.display_name,
            "status": s.status,
            "start_type": s.start_type,
            "pid": s.pid,
            "cpu_percent": s.cpu_percent / 100 if s.cpu_percent else None,
            "memory_mb": s.memory_mb,
            "description": s.description,
            "collected_at": s.collected_at.isoformat(),
        }
        for s in services
    ]


@router.get("/agents/{agent_id}/events")
async def get_agent_events(
    agent_id: int,
    limit: int = 200,
    level: Optional[str] = None,
    channel: Optional[str] = None,
    hours: int = 24,
    db: Session = Depends(get_db),
):
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    query = db.query(WindowsEvent).filter(
        WindowsEvent.agent_id == agent_id,
        WindowsEvent.recorded_at >= cutoff
    )
    if level:
        query = query.filter(WindowsEvent.level == level.upper())
    if channel:
        query = query.filter(WindowsEvent.channel == channel)

    events = query.order_by(WindowsEvent.recorded_at.desc()).limit(limit).all()
    return [
        {
            "event_id": e.event_id,
            "level": e.level,
            "source": e.source,
            "channel": e.channel,
            "message": e.message,
            "computer": e.computer,
            "recorded_at": e.recorded_at.isoformat(),
        }
        for e in events
    ]


@router.get("/agents/{agent_id}/logs")
async def get_agent_logs(
    agent_id: int,
    limit: int = 200,
    source: Optional[str] = None,
    level: Optional[str] = None,
    hours: int = 24,
    db: Session = Depends(get_db),
):
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    query = db.query(WindowsLogEntry).filter(
        WindowsLogEntry.agent_id == agent_id,
        WindowsLogEntry.timestamp >= cutoff
    )
    if source:
        query = query.filter(WindowsLogEntry.log_source == source)
    if level:
        query = query.filter(WindowsLogEntry.level == level.upper())

    logs = query.order_by(WindowsLogEntry.timestamp.desc()).limit(limit).all()
    return [
        {
            "log_source": l.log_source,
            "file_path": l.file_path,
            "level": l.level,
            "message": l.message,
            "timestamp": l.timestamp.isoformat(),
            "extra": l.extra,
        }
        for l in logs
    ]


@router.get("/summary")
async def agent_summary(db: Session = Depends(get_db)):
    """Dashboard summary: agent counts, status distribution"""
    from sqlalchemy import func as sqlfunc
    total = db.query(WindowsAgent).count()
    online = db.query(WindowsAgent).filter(WindowsAgent.status == "online").count()
    offline = db.query(WindowsAgent).filter(WindowsAgent.status == "offline").count()
    stale = db.query(WindowsAgent).filter(WindowsAgent.status == "stale").count()

    # Recent event counts
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(hours=24)
    events_24h = db.query(WindowsEvent).filter(WindowsEvent.recorded_at >= cutoff).count()
    errors_24h = db.query(WindowsEvent).filter(
        WindowsEvent.recorded_at >= cutoff,
        WindowsEvent.level.in_(["ERROR", "CRITICAL"])
    ).count()

    return {
        "agents": {"total": total, "online": online, "offline": offline, "stale": stale},
        "events_24h": events_24h,
        "errors_24h": errors_24h,
    }