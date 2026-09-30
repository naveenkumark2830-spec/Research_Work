from typing import List, Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session as DBSession
from app.db.database import get_db
from app.state.session_state import SessionState
from app.models.session import Session
from app.models.event import Event
from app.models.checkpoint import Checkpoint
from app.schemas.session import (
    CreateSessionRequest,
    AddMessageRequest,
    CreateCheckpointRequest,
    RestoreCheckpointRequest
)
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.repositories.session_repository import SQLAlchemySessionRepository
from app.repositories.event_repository import SQLAlchemyEventRepository
from app.repositories.checkpoint_repository import SQLAlchemyCheckpointRepository
from app.repositories.conversation_repository import SQLAlchemyConversationRepository

from app.services.session_service import SessionService
from app.services.state_service import StateService
from app.services.conversation_service import ConversationService
from app.services.checkpoint_service import CheckpointService
from app.services.event_service import EventService

router = APIRouter()


def get_services(db: DBSession = Depends(get_db)):
    user_repo = SQLAlchemyUserRepository(db)
    session_repo = SQLAlchemySessionRepository(db)
    event_repo = SQLAlchemyEventRepository(db)
    checkpoint_repo = SQLAlchemyCheckpointRepository(db)
    conversation_repo = SQLAlchemyConversationRepository(db)

    return {
        "session": SessionService(session_repo, user_repo, event_repo),
        "state": StateService(session_repo, event_repo),
        "conversation": ConversationService(session_repo, conversation_repo, event_repo),
        "checkpoint": CheckpointService(session_repo, checkpoint_repo, event_repo),
        "event": EventService(session_repo, event_repo, checkpoint_repo),
    }


@router.post("", response_model=SessionState, status_code=201, summary="Create Session")
def create_session(
    request: CreateSessionRequest,
    services: dict = Depends(get_services)
):
    return services["session"].create_session(
        user_id=request.user_id,
        current_topic=request.current_topic or "HDFS Architecture & Data Replication"
    )


@router.get("/{session_id}", response_model=Session, summary="Get Session Info")
def get_session(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    services: dict = Depends(get_services)
):
    state = services["session"].get_session_state(session_id, user_id=x_user_id)
    return state.session


@router.get("/{session_id}/state", response_model=SessionState, summary="Get Complete Session State")
def get_session_state(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    services: dict = Depends(get_services)
):
    target_user_id = x_user_id or user_id
    return services["session"].get_session_state(session_id, user_id=target_user_id)


@router.post("/{session_id}/start", response_model=SessionState, summary="Start Simulation")
def start_simulation(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    services: dict = Depends(get_services)
):
    target_user_id = x_user_id or user_id
    return services["state"].start_simulation(session_id, user_id=target_user_id)


@router.post("/{session_id}/pause", response_model=SessionState, summary="Pause Simulation")
def pause_simulation(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    services: dict = Depends(get_services)
):
    target_user_id = x_user_id or user_id
    return services["state"].pause_simulation(session_id, user_id=target_user_id)


@router.post("/{session_id}/resume", response_model=SessionState, summary="Resume Simulation")
def resume_simulation(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    services: dict = Depends(get_services)
):
    target_user_id = x_user_id or user_id
    return services["state"].resume_simulation(session_id, user_id=target_user_id)


@router.post("/{session_id}/restart", response_model=SessionState, summary="Restart Simulation")
def restart_simulation(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    services: dict = Depends(get_services)
):
    target_user_id = x_user_id or user_id
    return services["state"].restart_simulation(session_id, user_id=target_user_id)


@router.post("/{session_id}/checkpoint", response_model=Checkpoint, status_code=201, summary="Create Checkpoint")
def create_checkpoint(
    session_id: str,
    request: Optional[CreateCheckpointRequest] = None,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    services: dict = Depends(get_services)
):
    req_user_id = request.user_id if request else None
    target_user_id = x_user_id or req_user_id
    desc = request.description if (request and request.description) else "User state checkpoint"
    return services["checkpoint"].create_checkpoint(session_id, description=desc, user_id=target_user_id)


@router.get("/{session_id}/checkpoints", response_model=List[Checkpoint], summary="List Checkpoints")
def get_checkpoints(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    services: dict = Depends(get_services)
):
    target_user_id = x_user_id or user_id
    return services["checkpoint"].get_checkpoints(session_id, user_id=target_user_id)


@router.post("/{session_id}/restore/{checkpoint_id}", response_model=SessionState, summary="Restore Checkpoint State")
def restore_checkpoint(
    session_id: str,
    checkpoint_id: str,
    request: Optional[RestoreCheckpointRequest] = None,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    services: dict = Depends(get_services)
):
    req_user_id = request.user_id if request else None
    target_user_id = x_user_id or req_user_id
    return services["checkpoint"].restore_checkpoint(session_id, checkpoint_id, user_id=target_user_id)


@router.get("/{session_id}/events", response_model=List[Event], summary="List Session Event History")
def get_events(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    services: dict = Depends(get_services)
):
    target_user_id = x_user_id or user_id
    return services["event"].get_session_events(session_id, user_id=target_user_id)


@router.post("/{session_id}/messages", response_model=SessionState, summary="Add Message to Conversation")
def add_message(
    session_id: str,
    request: AddMessageRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    services: dict = Depends(get_services)
):
    target_user_id = x_user_id or request.user_id
    return services["conversation"].add_message(
        session_id=session_id,
        role=request.role,
        content=request.content,
        user_id=target_user_id
    )
