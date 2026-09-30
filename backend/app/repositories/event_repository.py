from abc import ABC, abstractmethod
import json
from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session as DBSession
from app.models.event import Event, EventCategory
from app.db.models import EventModel


class IEventRepository(ABC):
    @abstractmethod
    def save(self, event: Event) -> Event:
        pass

    @abstractmethod
    def get_by_id(self, event_id: str) -> Optional[Event]:
        pass

    @abstractmethod
    def get_by_session(self, session_id: str) -> List[Event]:
        pass

    @abstractmethod
    def get_by_sequence_range(self, session_id: str, start_seq: int, end_seq: int) -> List[Event]:
        pass

    @abstractmethod
    def get_by_type(self, session_id: str, event_type: str) -> List[Event]:
        pass

    @abstractmethod
    def get_by_category(self, session_id: str, category: str) -> List[Event]:
        pass

    @abstractmethod
    def get_latest_event(self, session_id: str) -> Optional[Event]:
        pass

    @abstractmethod
    def get_event_count(self, session_id: str) -> int:
        pass

    @abstractmethod
    def get_next_sequence_number(self, session_id: str) -> int:
        pass


class SQLAlchemyEventRepository(IEventRepository):
    def __init__(self, db: DBSession):
        self.db = db

    def _to_domain(self, e: EventModel) -> Event:
        category_val = getattr(e, "category", "SYSTEM")
        cat_enum = EventCategory(category_val) if category_val in EventCategory.__members__ else EventCategory.SYSTEM
        return Event(
            event_id=e.event_id,
            session_id=e.session_id,
            category=cat_enum,
            event_type=e.event_type,
            sequence_number=e.sequence_number,
            logical_timestamp=getattr(e, "logical_timestamp", 0.0),
            timestamp=e.timestamp,
            created_at=getattr(e, "timestamp", e.timestamp),
            state_version=e.state_version,
            payload=json.loads(e.payload_json or "{}")
        )

    def save(self, event: Event) -> Event:
        db_event = EventModel(
            event_id=event.event_id,
            session_id=event.session_id,
            category=event.category.value if isinstance(event.category, EventCategory) else str(event.category),
            event_type=str(event.event_type.value) if hasattr(event.event_type, "value") else str(event.event_type),
            timestamp=event.timestamp,
            logical_timestamp=event.logical_timestamp,
            sequence_number=event.sequence_number,
            payload_json=json.dumps(event.payload),
            state_version=event.state_version
        )
        self.db.add(db_event)
        self.db.commit()
        return event

    def get_by_id(self, event_id: str) -> Optional[Event]:
        db_event = self.db.query(EventModel).filter(EventModel.event_id == event_id).first()
        if not db_event:
            return None
        return self._to_domain(db_event)

    def get_by_session(self, session_id: str) -> List[Event]:
        db_events = (
            self.db.query(EventModel)
            .filter(EventModel.session_id == session_id)
            .order_by(EventModel.sequence_number.asc())
            .all()
        )
        return [self._to_domain(e) for e in db_events]

    def get_by_sequence_range(self, session_id: str, start_seq: int, end_seq: int) -> List[Event]:
        db_events = (
            self.db.query(EventModel)
            .filter(
                EventModel.session_id == session_id,
                EventModel.sequence_number >= start_seq,
                EventModel.sequence_number <= end_seq
            )
            .order_by(EventModel.sequence_number.asc())
            .all()
        )
        return [self._to_domain(e) for e in db_events]

    def get_by_type(self, session_id: str, event_type: str) -> List[Event]:
        db_events = (
            self.db.query(EventModel)
            .filter(EventModel.session_id == session_id, EventModel.event_type == event_type)
            .order_by(EventModel.sequence_number.asc())
            .all()
        )
        return [self._to_domain(e) for e in db_events]

    def get_by_category(self, session_id: str, category: str) -> List[Event]:
        db_events = (
            self.db.query(EventModel)
            .filter(EventModel.session_id == session_id, EventModel.category == category)
            .order_by(EventModel.sequence_number.asc())
            .all()
        )
        return [self._to_domain(e) for e in db_events]

    def get_latest_event(self, session_id: str) -> Optional[Event]:
        db_event = (
            self.db.query(EventModel)
            .filter(EventModel.session_id == session_id)
            .order_by(EventModel.sequence_number.desc())
            .first()
        )
        if not db_event:
            return None
        return self._to_domain(db_event)

    def get_event_count(self, session_id: str) -> int:
        return self.db.query(EventModel).filter(EventModel.session_id == session_id).count()

    def get_next_sequence_number(self, session_id: str) -> int:
        max_seq = (
            self.db.query(func.max(EventModel.sequence_number))
            .filter(EventModel.session_id == session_id)
            .scalar()
        )
        return (max_seq or 0) + 1
