from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import BaseModel, Field


class Checkpoint(BaseModel):
    checkpoint_id: str
    session_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sequence_number: int
    state_snapshot: Dict[str, Any]
    description: str = "Session State Checkpoint"
