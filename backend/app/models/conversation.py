from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"


class Message(BaseModel):
    message_id: str
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationState(BaseModel):
    current_topic: str = "HDFS Architecture & Data Replication"
    current_intent: Optional[str] = None
    last_user_message: Optional[str] = None
    last_assistant_message: Optional[str] = None
    last_question: Optional[str] = None
    conversation_turn_count: int = 0
    recent_messages: List[Message] = Field(default_factory=list)
