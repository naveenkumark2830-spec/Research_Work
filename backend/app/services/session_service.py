import uuid
from datetime import datetime, timezone
from typing import Optional, List
from app.models.session import Session, SessionStatus
from app.models.event import Event, EventType
from app.state.session_state import SessionState
from app.core.exceptions import ResourceNotFoundError, UserIsolationError
from app.repositories.user_repository import IUserRepository
from app.repositories.session_repository import ISessionRepository
from app.repositories.event_repository import IEventRepository


class SessionService:
    def __init__(
        self,
        session_repo: ISessionRepository,
        user_repo: IUserRepository,
        event_repo: IEventRepository
    ):
        self.session_repo = session_repo
        self.user_repo = user_repo
        self.event_repo = event_repo

    def create_session(self, user_id: str, current_topic: str = "HDFS Fundamentals") -> SessionState:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ResourceNotFoundError("User", user_id)

        session_id = f"ses_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
            last_activity_at=now,
            status=SessionStatus.ACTIVE,
            current_topic=current_topic
        )

        state = SessionState(
            user=user,
            session=session,
            state_version=1
        )

        self.session_repo.save_state(state)

        # Record SESSION_CREATED event
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            event_type=EventType.SESSION_CREATED,
            timestamp=now,
            sequence_number=1,
            payload={"user_id": user_id, "topic": current_topic},
            state_version=1
        )
        self.event_repo.save(event)

        return state

    def get_session_state(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)
        return state

    def list_user_sessions(self, user_id: str) -> List[Session]:
        return self.session_repo.list_user_sessions(user_id)
