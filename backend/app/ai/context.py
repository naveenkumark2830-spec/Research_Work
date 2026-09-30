from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AIContext(BaseModel):
    """Controlled, session-scoped context model passed to AI providers."""

    user_message: str
    user_context: Dict[str, Any] = Field(default_factory=dict)
    session_context: Dict[str, Any] = Field(default_factory=dict)
    conversation_context: Dict[str, Any] = Field(default_factory=dict)
    simulation_state: Dict[str, Any] = Field(default_factory=dict)
    visualization_state: Dict[str, Any] = Field(default_factory=dict)
    event_context: Dict[str, Any] = Field(default_factory=dict)
