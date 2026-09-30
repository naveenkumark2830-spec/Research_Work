from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DBSession

from app.db.database import get_db
from app.repositories.session_repository import SQLAlchemySessionRepository
from app.repositories.event_repository import SQLAlchemyEventRepository
from app.services.hdfs_service import HDFSService
from app.services.state_service import StateService
from app.ai.orchestrator import AIOrchestrator, OrchestrationResponse
from app.jarvis.schemas import TeddyResponse

router = APIRouter()


class AIMessageRequest(BaseModel):
    user_id: Optional[str] = None
    message: str = Field(..., json_schema_extra={"example": "Set the block size to 256 MB."})
    visualization_context: Optional[Dict[str, Any]] = Field(default_factory=dict)


def get_ai_orchestrator(db: DBSession = Depends(get_db)) -> AIOrchestrator:
    session_repo = SQLAlchemySessionRepository(db)
    event_repo = SQLAlchemyEventRepository(db)
    hdfs_service = HDFSService(session_repo, event_repo)
    state_service = StateService(session_repo, event_repo)
    return AIOrchestrator(session_repo, event_repo, hdfs_service, state_service)


@router.post("/sessions/{session_id}/message", response_model=OrchestrationResponse, summary="Send Natural Language Message to JARVIS AI Orchestrator")
def send_ai_message(
    session_id: str,
    request: AIMessageRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    orchestrator: AIOrchestrator = Depends(get_ai_orchestrator)
):
    target_user_id = x_user_id or request.user_id
    return orchestrator.process_message(
        session_id=session_id,
        message=request.message,
        user_id=target_user_id,
        visualization_context=request.visualization_context
    )


# ---------------------------------------------------------
# Teddy AI Orchestrator API (Stage 8.7 & 8.8)
# ---------------------------------------------------------

class AIChatRequest(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    message: str = Field(..., json_schema_extra={"example": "What does the NameNode do?"})


@router.post("/chat", response_model=TeddyResponse, summary="Teddy AI Orchestrator Chat")
async def teddy_ai_chat(
    request: AIChatRequest,
    db: DBSession = Depends(get_db)
):
    from app.jarvis.provider import create_teddy_orchestrator
    from app.jarvis.schemas import TeddyRequest

    session_repo = SQLAlchemySessionRepository(db)
    event_repo = SQLAlchemyEventRepository(db)
    hdfs_service = HDFSService(session_repo, event_repo)

    orchestrator = create_teddy_orchestrator(hdfs_service=hdfs_service)

    teddy_request = TeddyRequest(
        session_id=request.session_id,
        user_id=request.user_id,
        message=request.message,
    )

    return await orchestrator.process(teddy_request)
