from typing import List, Optional, Dict, Any
from app.models.event import Event, EventCategory
from app.state.session_state import SessionState
from app.core.exceptions import ResourceNotFoundError, UserIsolationError
from app.repositories.session_repository import ISessionRepository
from app.repositories.event_repository import IEventRepository
from app.repositories.checkpoint_repository import ICheckpointRepository
from app.events.engine import EventEngine
from app.events.replayer import EventReplayer
from app.events.cursor import PlaybackController, EventCursor


class EventService:
    def __init__(
        self,
        session_repo: ISessionRepository,
        event_repo: IEventRepository,
        checkpoint_repo: ICheckpointRepository
    ):
        self.session_repo = session_repo
        self.event_repo = event_repo
        self.checkpoint_repo = checkpoint_repo
        self.engine = EventEngine(event_repo)
        self.replayer = EventReplayer(session_repo, event_repo, checkpoint_repo)
        self.playback = PlaybackController(session_repo, event_repo)

    def get_event(self, event_id: str) -> Event:
        return self.engine.get_event(event_id)

    def get_session_events(self, session_id: str, user_id: Optional[str] = None) -> List[Event]:
        self._verify_user_access(session_id, user_id)
        return self.engine.get_events(session_id)

    def get_events_range(self, session_id: str, start_seq: int, end_seq: int, user_id: Optional[str] = None) -> List[Event]:
        self._verify_user_access(session_id, user_id)
        return self.engine.get_events_range(session_id, start_seq, end_seq)

    def get_events_by_type(self, session_id: str, event_type: str, user_id: Optional[str] = None) -> List[Event]:
        self._verify_user_access(session_id, user_id)
        return self.engine.get_events_by_type(session_id, event_type)

    def get_events_by_category(self, session_id: str, category: str, user_id: Optional[str] = None) -> List[Event]:
        self._verify_user_access(session_id, user_id)
        return self.engine.get_events_by_category(session_id, category)

    def get_timeline(self, session_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        self._verify_user_access(session_id, user_id)
        events = self.engine.get_events(session_id)
        cursor = self.playback.get_cursor(session_id, user_id=user_id)

        return {
            "session_id": session_id,
            "total_events": len(events),
            "current_sequence": cursor.current_sequence,
            "current_logical_time": cursor.current_logical_time,
            "current_state_version": cursor.current_state_version,
            "status": cursor.status.value,
            "events": [
                {
                    "event_id": e.event_id,
                    "sequence_number": e.sequence_number,
                    "category": e.category.value if hasattr(e.category, "value") else str(e.category),
                    "event_type": str(e.event_type.value) if hasattr(e.event_type, "value") else str(e.event_type),
                    "logical_timestamp": e.logical_timestamp,
                    "state_version": e.state_version,
                    "payload": e.payload
                }
                for e in events
            ]
        }

    def replay_events(
        self,
        session_id: str,
        target_sequence: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        replayed_state = self.replayer.replay_events(session_id, target_sequence=target_sequence, user_id=user_id)
        return {
            "session_id": session_id,
            "target_sequence": target_sequence,
            "replayed_state": replayed_state.model_dump(mode="json"),
            "state_version": replayed_state.state_version
        }

    def replay_from_checkpoint(
        self,
        session_id: str,
        checkpoint_id: str,
        target_sequence: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        replayed_state = self.replayer.replay_from_checkpoint(
            session_id, checkpoint_id, target_sequence=target_sequence, user_id=user_id
        )
        return {
            "session_id": session_id,
            "checkpoint_id": checkpoint_id,
            "target_sequence": target_sequence,
            "replayed_state": replayed_state.model_dump(mode="json"),
            "state_version": replayed_state.state_version
        }

    def get_cursor(self, session_id: str, user_id: Optional[str] = None) -> EventCursor:
        return self.playback.get_cursor(session_id, user_id=user_id)

    def pause_cursor(self, session_id: str, user_id: Optional[str] = None) -> EventCursor:
        return self.playback.pause(session_id, user_id=user_id)

    def resume_cursor(self, session_id: str, user_id: Optional[str] = None) -> EventCursor:
        return self.playback.resume(session_id, user_id=user_id)

    def restart_cursor(self, session_id: str, user_id: Optional[str] = None) -> EventCursor:
        return self.playback.restart(session_id, user_id=user_id)

    def _verify_user_access(self, session_id: str, user_id: Optional[str] = None) -> None:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)
