from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, Header, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session as DBSession
from app.db.database import get_db
from app.models.event import Event
from app.events.cursor import EventCursor
from app.repositories.session_repository import SQLAlchemySessionRepository
from app.repositories.event_repository import SQLAlchemyEventRepository
from app.repositories.checkpoint_repository import SQLAlchemyCheckpointRepository
from app.services.event_service import EventService

router = APIRouter()


def get_event_service(db: DBSession = Depends(get_db)) -> EventService:
    session_repo = SQLAlchemySessionRepository(db)
    event_repo = SQLAlchemyEventRepository(db)
    checkpoint_repo = SQLAlchemyCheckpointRepository(db)
    return EventService(session_repo, event_repo, checkpoint_repo)


class ReplayRequest(BaseModel):
    user_id: Optional[str] = None
    target_sequence: Optional[int] = Field(default=None, json_schema_extra={"example": 43})
    checkpoint_id: Optional[str] = Field(default=None, json_schema_extra={"example": "chk_12345"})


@router.get("/{session_id}/events", response_model=List[Event], summary="List Session Event History")
def get_session_events(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or user_id
    return service.get_session_events(session_id, user_id=target_user_id)


@router.get("/{session_id}/events/range", response_model=List[Event], summary="Get Events by Sequence Range")
def get_events_range(
    session_id: str,
    start_seq: int = Query(1, ge=1),
    end_seq: int = Query(100, ge=1),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or user_id
    return service.get_events_range(session_id, start_seq, end_seq, user_id=target_user_id)


@router.get("/{session_id}/events/type/{event_type}", response_model=List[Event], summary="Get Events by Type")
def get_events_by_type(
    session_id: str,
    event_type: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or user_id
    return service.get_events_by_type(session_id, event_type, user_id=target_user_id)


@router.get("/{session_id}/timeline", summary="Get Structured Event Timeline")
def get_timeline(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or user_id
    return service.get_timeline(session_id, user_id=target_user_id)


@router.get("/{session_id}/cursor", response_model=EventCursor, summary="Get Timeline Playback Cursor")
def get_cursor(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or user_id
    return service.get_cursor(session_id, user_id=target_user_id)


@router.post("/{session_id}/cursor/pause", response_model=EventCursor, summary="Pause Timeline Playback")
def pause_cursor(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or user_id
    return service.pause_cursor(session_id, user_id=target_user_id)


@router.post("/{session_id}/cursor/resume", response_model=EventCursor, summary="Resume Timeline Playback")
def resume_cursor(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or user_id
    return service.resume_cursor(session_id, user_id=target_user_id)


@router.post("/{session_id}/cursor/restart", response_model=EventCursor, summary="Restart Timeline Playback")
def restart_cursor(
    session_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    user_id: Optional[str] = None,
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or user_id
    return service.restart_cursor(session_id, user_id=target_user_id)


@router.post("/{session_id}/replay", summary="Replay State at Target Sequence (Read-Only Inspection)")
def replay_events(
    session_id: str,
    request: ReplayRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    service: EventService = Depends(get_event_service)
):
    target_user_id = x_user_id or request.user_id
    if request.checkpoint_id:
        return service.replay_from_checkpoint(
            session_id, request.checkpoint_id, target_sequence=request.target_sequence, user_id=target_user_id
        )
    return service.replay_events(session_id, target_sequence=request.target_sequence, user_id=target_user_id)
