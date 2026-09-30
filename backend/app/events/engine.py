import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.exc import IntegrityError
from app.models.event import Event, EventCategory
from app.core.exceptions import InvalidStateTransitionError, ResourceNotFoundError
from app.repositories.event_repository import IEventRepository


class EventEngine:
    """Core Event Engine responsible for recording, ordering, validating, and persisting events."""

    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def validate_event_data(
        self,
        session_id: str,
        event_type: str,
        payload: Dict[str, Any],
        sequence_number: Optional[int] = None
    ) -> None:
        if not session_id or not session_id.strip():
            raise InvalidStateTransitionError("INVALID_SESSION", "APPEND_EVENT", ["VALID_SESSION_ID"])
        if not event_type or not str(event_type).strip():
            raise InvalidStateTransitionError("MISSING_EVENT_TYPE", "APPEND_EVENT", ["VALID_EVENT_TYPE"])
        if payload is None or not isinstance(payload, dict):
            raise InvalidStateTransitionError("INVALID_PAYLOAD", "APPEND_EVENT", ["DICT_PAYLOAD"])
        if sequence_number is not None and sequence_number < 1:
            raise InvalidStateTransitionError("INVALID_SEQUENCE", "APPEND_EVENT", ["SEQUENCE_GT_ZERO"])

    def append_event(
        self,
        session_id: str,
        event_type: str,
        payload: Dict[str, Any],
        category: EventCategory = EventCategory.SYSTEM,
        logical_timestamp: float = 0.0,
        state_version: int = 1,
        event_id: Optional[str] = None
    ) -> Event:
        self.validate_event_data(session_id, event_type, payload)

        now = datetime.now(timezone.utc)
        seq_num = self.event_repo.get_next_sequence_number(session_id)
        evt_id = event_id or f"evt_{uuid.uuid4().hex[:12]}"

        event = Event(
            event_id=evt_id,
            session_id=session_id,
            category=category,
            event_type=str(event_type.value) if hasattr(event_type, "value") else str(event_type),
            sequence_number=seq_num,
            logical_timestamp=logical_timestamp,
            timestamp=now,
            created_at=now,
            state_version=state_version,
            payload=payload
        )

        try:
            return self.event_repo.save(event)
        except IntegrityError:
            # Handle rare sequence collision cleanly by retrying next sequence
            seq_num_retry = self.event_repo.get_next_sequence_number(session_id)
            event.sequence_number = seq_num_retry
            return self.event_repo.save(event)

    def get_event(self, event_id: str) -> Event:
        evt = self.event_repo.get_by_id(event_id)
        if not evt:
            raise ResourceNotFoundError("Event", event_id)
        return evt

    def get_events(self, session_id: str) -> List[Event]:
        return self.event_repo.get_by_session(session_id)

    def get_events_range(self, session_id: str, start_seq: int, end_seq: int) -> List[Event]:
        return self.event_repo.get_by_sequence_range(session_id, start_seq, end_seq)

    def get_events_by_type(self, session_id: str, event_type: str) -> List[Event]:
        return self.event_repo.get_by_type(session_id, event_type)

    def get_events_by_category(self, session_id: str, category: str) -> List[Event]:
        return self.event_repo.get_by_category(session_id, category)

    def get_latest_event(self, session_id: str) -> Optional[Event]:
        return self.event_repo.get_latest_event(session_id)

    def get_event_count(self, session_id: str) -> int:
        return self.event_repo.get_event_count(session_id)
