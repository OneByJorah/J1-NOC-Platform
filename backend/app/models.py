from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text,
    ForeignKey,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    permissions = Column(JSON, nullable=False, default={})
    is_system = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    contact_email = Column(String(255))
    contact_phone = Column(String(255))
    address = Column(Text)
    tenant_id = Column(String(255), nullable=False, default="default")
    is_active = Column(Boolean, nullable=False, default=True)
    extra_metadata = Column("metadata", JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(Text)
    timezone = Column(String(64), nullable=False, default="UTC")
    extra_metadata = Column("metadata", JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255))
    full_name = Column(String(255))
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="SET NULL"))
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"))
    is_active = Column(Boolean, nullable=False, default=True)
    is_locked = Column(Boolean, nullable=False, default=False)
    last_login_at = Column(DateTime(timezone=True))
    extra_metadata = Column("metadata", JSON, nullable=False, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    role = relationship("Role", lazy="joined")


# ===================== WINDOWS AGENT MODELS =====================

class WindowsAgent(Base):
    """Registered Windows agent endpoints"""
    __tablename__ = "windows_agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(128), unique=True, nullable=False, index=True)  # UUID from agent
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(64))
    os_version = Column(String(128))
    agent_version = Column(String(32))
    status = Column(String(32), default="unknown")  # online, offline, stale
    last_seen = Column(DateTime(timezone=True))
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    config = Column(JSON, nullable=False, default={})  # agent-specific config
    tags = Column(JSON, nullable=False, default=[])  # e.g., ["prod", "dc", "fileserver"]

    # Relationships
    services = relationship("WindowsService", back_populates="agent", cascade="all, delete-orphan")
    events = relationship("WindowsEvent", back_populates="agent", cascade="all, delete-orphan")
    logs = relationship("WindowsLogEntry", back_populates="agent", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_windows_agents_hostname", "hostname"),
        Index("ix_windows_agents_status", "status"),
    )


class WindowsService(Base):
    """Windows service status snapshots"""
    __tablename__ = "windows_services"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("windows_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    service_name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255))
    status = Column(String(32), nullable=False)  # running, stopped, paused, start_pending, stop_pending
    start_type = Column(String(32))  # automatic, manual, disabled
    pid = Column(Integer)
    cpu_percent = Column(Integer)  # scaled by 100 (e.g., 1500 = 15.00%)
    memory_mb = Column(Integer)
    description = Column(Text)
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    agent = relationship("WindowsAgent", back_populates="services")

    __table_args__ = (
        Index("ix_windows_services_agent_collected", "agent_id", "collected_at"),
        Index("ix_windows_services_name_status", "service_name", "status"),
    )


class WindowsEvent(Base):
    """Windows Event Log entries (System, Application, Security, etc.)"""
    __tablename__ = "windows_events"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("windows_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, nullable=False)  # Windows Event ID
    level = Column(String(16), nullable=False)  # ERROR, WARNING, INFORMATION, CRITICAL
    source = Column(String(255), nullable=False, index=True)  # Event Source/Provider
    channel = Column(String(64), nullable=False)  # System, Application, Security, etc.
    message = Column(Text, nullable=False)
    computer = Column(String(255))
    user_sid = Column(String(128))
    category = Column(String(128))
    raw_xml = Column(Text)  # Full event XML for debugging
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)  # When event occurred
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    agent = relationship("WindowsAgent", back_populates="events")

    __table_args__ = (
        Index("ix_windows_events_agent_recorded", "agent_id", "recorded_at"),
        Index("ix_windows_events_level_channel", "level", "channel"),
        Index("ix_windows_events_source_recorded", "source", "recorded_at"),
    )


class WindowsLogEntry(Base):
    """Generic log file entries (e.g., Google CloudSync logs, custom app logs)"""
    __tablename__ = "windows_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("windows_agents.id", ondelete="CASCADE"), nullable=False, index=True)
    log_source = Column(String(128), nullable=False, index=True)  # e.g., "googledrive", "custom_app"
    file_path = Column(String(512))
    level = Column(String(16))  # ERROR, WARNING, INFO, DEBUG
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)  # Parsed from log line
    collected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    extra = Column(JSON, nullable=False, default={})  # Parsed key-value pairs

    agent = relationship("WindowsAgent", back_populates="logs")

    __table_args__ = (
        Index("ix_windows_logs_agent_timestamp", "agent_id", "timestamp"),
        Index("ix_windows_logs_source_level", "log_source", "level"),
    )


# ===================== TABS / NAVIGATION =====================

class Tab(Base):
    __tablename__ = "tabs"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(128), unique=True, nullable=False, index=True)
    label = Column(String(128), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    is_visible = Column(Boolean, nullable=False, default=True)
    icon = Column(String(64), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())