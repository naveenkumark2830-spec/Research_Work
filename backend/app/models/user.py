from datetime import datetime, timezone
from typing import Dict, Any
from pydantic import BaseModel, Field


class User(BaseModel):
    user_id: str
    display_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    preferences: Dict[str, Any] = Field(default_factory=dict)
