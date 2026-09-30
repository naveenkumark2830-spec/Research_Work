from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.user import User


class CreateUserRequest(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=128, json_schema_extra={"example": "Hadoop Explorer"})
    preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UserResponse(BaseModel):
    user: User
