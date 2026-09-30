from abc import ABC, abstractmethod
import json
from typing import Optional, List
from sqlalchemy.orm import Session as DBSession
from app.state.session_state import SessionState
from app.models.session import Session, SessionStatus
from app.db.models import SessionModel


class ISessionRepository(ABC):
    @abstractmethod
    def save_state(self, state: SessionState) -> SessionState:
        pass

    @abstractmethod
    def get_state(self, session_id: str) -> Optional[SessionState]:
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Session]:
        pass

    @abstractmethod
    def list_user_sessions(self, user_id: str) -> List[Session]:
        pass


class SQLAlchemySessionRepository(ISessionRepository):
    def __init__(self, db: DBSession):
        self.db = db

    def save_state(self, state: SessionState) -> SessionState:
        state_dict = state.model_dump(mode="json")
        state_json = json.dumps(state_dict)

        db_session = self.db.query(SessionModel).filter(SessionModel.session_id == state.session.session_id).first()
        if db_session:
            db_session.status = state.session.status.value
            db_session.current_topic = state.session.current_topic
            db_session.updated_at = state.session.updated_at
            db_session.last_activity_at = state.session.last_activity_at
            db_session.state_version = state.state_version
            db_session.state_json = state_json
        else:
            db_session = SessionModel(
                session_id=state.session.session_id,
                user_id=state.session.user_id,
                created_at=state.session.created_at,
                updated_at=state.session.updated_at,
                last_activity_at=state.session.last_activity_at,
                status=state.session.status.value,
                current_topic=state.session.current_topic,
                state_version=state.state_version,
                state_json=state_json
            )
            self.db.add(db_session)

        self.db.commit()
        return state

    def get_state(self, session_id: str) -> Optional[SessionState]:
        db_session = self.db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not db_session:
            return None
        state_dict = json.loads(db_session.state_json)
        return SessionState.model_validate(state_dict)

    def get_session(self, session_id: str) -> Optional[Session]:
        db_session = self.db.query(SessionModel).filter(SessionModel.session_id == session_id).first()
        if not db_session:
            return None
        return Session(
            session_id=db_session.session_id,
            user_id=db_session.user_id,
            created_at=db_session.created_at,
            updated_at=db_session.updated_at,
            last_activity_at=db_session.last_activity_at,
            status=SessionStatus(db_session.status),
            current_topic=db_session.current_topic
        )

    def list_user_sessions(self, user_id: str) -> List[Session]:
        db_sessions = self.db.query(SessionModel).filter(SessionModel.user_id == user_id).all()
        return [
            Session(
                session_id=s.session_id,
                user_id=s.user_id,
                created_at=s.created_at,
                updated_at=s.updated_at,
                last_activity_at=s.last_activity_at,
                status=SessionStatus(s.status),
                current_topic=s.current_topic
            )
            for s in db_sessions
        ]
