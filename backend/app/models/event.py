from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class EventCategory(str, Enum):
    SESSION = "SESSION"
    CONVERSATION = "CONVERSATION"
    SIMULATION = "SIMULATION"
    HDFS = "HDFS"
    VISUALIZATION = "VISUALIZATION"
    VOICE = "VOICE"
    LEARNING = "LEARNING"
    SYSTEM = "SYSTEM"


class EventType(str, Enum):
    SESSION_CREATED = "SESSION_CREATED"
    SESSION_UPDATED = "SESSION_UPDATED"
    CONVERSATION_MESSAGE_ADDED = "CONVERSATION_MESSAGE_ADDED"
    SIMULATION_STARTED = "SIMULATION_STARTED"
    SIMULATION_PAUSED = "SIMULATION_PAUSED"
    SIMULATION_RESUMED = "SIMULATION_RESUMED"
    SIMULATION_RESTARTED = "SIMULATION_RESTARTED"
    VISUALIZATION_UPDATED = "VISUALIZATION_UPDATED"
    VOICE_INTERRUPTED = "VOICE_INTERRUPTED"
    CHECKPOINT_CREATED = "CHECKPOINT_CREATED"
    STATE_RESTORED = "STATE_RESTORED"
    SIMULATION_UPDATED = "SIMULATION_UPDATED"
    SIMULATION_CONFIG_UPDATED = "SIMULATION_CONFIG_UPDATED"
    DATANODE_ADDED = "DATANODE_ADDED"
    DATANODE_REMOVED = "DATANODE_REMOVED"
    SIMULATION_SPEED_CHANGED = "SIMULATION_SPEED_CHANGED"


class Event(BaseModel):
    event_id: str
    session_id: str
    category: EventCategory = EventCategory.SYSTEM
    event_type: str  # Can be EventType or HDFSEventType string
    sequence_number: int
    logical_timestamp: float = 0.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    state_version: int = 1
    payload: Dict[str, Any] = Field(default_factory=dict)
