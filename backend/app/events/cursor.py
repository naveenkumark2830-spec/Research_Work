from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.event import Event
from app.repositories.event_repository import IEventRepository
from app.repositories.session_repository import ISessionRepository
from app.core.exceptions import ResourceNotFoundError, UserIsolationError


class PlaybackStatus(str, Enum):
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"


class EventCursor(BaseModel):
    session_id: str
    current_sequence: int = 0
    current_logical_time: float = 0.0
    current_state_version: int = 1
    total_events: int = 0
    status: PlaybackStatus = PlaybackStatus.IDLE


class PlaybackController:
    """Manages timeline playback, cursor navigation, and pause/resume controls."""

    def __init__(self, session_repo: ISessionRepository, event_repo: IEventRepository):
        self.session_repo = session_repo
        self.event_repo = event_repo

    def get_cursor(self, session_id: str, user_id: Optional[str] = None) -> EventCursor:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        latest_evt = self.event_repo.get_latest_event(session_id)
        total = self.event_repo.get_event_count(session_id)

        raw_cursor = state.simulation.configuration.custom_parameters.get("playback_cursor")
        if raw_cursor:
            cursor = EventCursor.model_validate(raw_cursor)
            cursor.total_events = total
            return cursor

        return EventCursor(
            session_id=session_id,
            current_sequence=latest_evt.sequence_number if latest_evt else 0,
            current_logical_time=latest_evt.logical_timestamp if latest_evt else 0.0,
            current_state_version=state.state_version,
            total_events=total,
            status=PlaybackStatus.IDLE if state.simulation.status.value != "RUNNING" else PlaybackStatus.PLAYING
        )

    def _save_cursor(self, session_id: str, cursor: EventCursor, user_id: Optional[str] = None) -> EventCursor:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        state.simulation.configuration.custom_parameters["playback_cursor"] = cursor.model_dump(mode="json")
        self.session_repo.save_state(state)
        return cursor

    def pause(self, session_id: str, user_id: Optional[str] = None) -> EventCursor:
        cursor = self.get_cursor(session_id, user_id=user_id)
        cursor.status = PlaybackStatus.PAUSED
        return self._save_cursor(session_id, cursor, user_id=user_id)

    def resume(self, session_id: str, user_id: Optional[str] = None) -> EventCursor:
        cursor = self.get_cursor(session_id, user_id=user_id)
        cursor.status = PlaybackStatus.PLAYING
        return self._save_cursor(session_id, cursor, user_id=user_id)

    def restart(self, session_id: str, user_id: Optional[str] = None) -> EventCursor:
        cursor = self.get_cursor(session_id, user_id=user_id)
        cursor.current_sequence = 0
        cursor.current_logical_time = 0.0
        cursor.status = PlaybackStatus.PLAYING
        return self._save_cursor(session_id, cursor, user_id=user_id)
