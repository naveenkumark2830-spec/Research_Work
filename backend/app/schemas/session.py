from typing import Optional
from pydantic import BaseModel, Field
from app.models.conversation import MessageRole


class CreateSessionRequest(BaseModel):
    user_id: str = Field(..., json_schema_extra={"example": "usr_12345678"})
    current_topic: Optional[str] = Field(default="HDFS Architecture & Data Replication")


class AddMessageRequest(BaseModel):
    user_id: Optional[str] = None
    role: MessageRole = MessageRole.USER
    content: str = Field(..., min_length=1, json_schema_extra={"example": "Why are there three replicas in default HDFS?"})


class CreateCheckpointRequest(BaseModel):
    user_id: Optional[str] = None
    description: Optional[str] = Field(default="User state checkpoint")


class RestoreCheckpointRequest(BaseModel):
    user_id: Optional[str] = None


class UserHeader(BaseModel):
    user_id: Optional[str] = None
