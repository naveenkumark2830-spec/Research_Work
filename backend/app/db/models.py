from datetime import datetime, timezone
import json
from typing import Dict, Any
from sqlalchemy import String, DateTime, Integer, Text, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from app.models.session import SessionStatus


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    preferences_json: Mapped[str] = mapped_column(Text, default="{}")

    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")


class SessionModel(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(64), ForeignKey("users.user_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    status: Mapped[str] = mapped_column(String(32), default=SessionStatus.ACTIVE.value)
    current_topic: Mapped[str] = mapped_column(String(256), default="HDFS Fundamentals")
    state_version: Mapped[int] = mapped_column(Integer, default=1)
    state_json: Mapped[str] = mapped_column(Text, nullable=False)

    user = relationship("UserModel", back_populates="sessions")
    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan")
    events = relationship("EventModel", back_populates="session", cascade="all, delete-orphan")
    checkpoints = relationship("CheckpointModel", back_populates="session", cascade="all, delete-orphan")


class MessageModel(Base):
    __tablename__ = "messages"

    message_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("sessions.session_id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    session = relationship("SessionModel", back_populates="messages")


class EventModel(Base):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("session_id", "sequence_number", name="uix_session_sequence"),
    )

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("sessions.session_id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(32), default="SYSTEM", nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    logical_timestamp: Mapped[float] = mapped_column(Float, default=0.0)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    state_version: Mapped[int] = mapped_column(Integer, nullable=False)

    session = relationship("SessionModel", back_populates="events")


class CheckpointModel(Base):
    __tablename__ = "checkpoints"

    checkpoint_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String(64), ForeignKey("sessions.session_id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    state_snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(String(256), default="Session State Checkpoint")

    session = relationship("SessionModel", back_populates="checkpoints")
