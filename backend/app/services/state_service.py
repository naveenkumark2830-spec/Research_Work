import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.state.session_state import SessionState
from app.state.state_machine import StateMachine
from app.models.event import Event, EventType
from app.core.exceptions import ResourceNotFoundError, UserIsolationError
from app.repositories.session_repository import ISessionRepository
from app.repositories.event_repository import IEventRepository


class StateService:
    def __init__(
        self,
        session_repo: ISessionRepository,
        event_repo: IEventRepository
    ):
        self.session_repo = session_repo
        self.event_repo = event_repo

    def get_state(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)
        return state

    def _execute_transition(
        self,
        session_id: str,
        transition_fn,
        payload: Dict[str, Any],
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.get_state(session_id, user_id=user_id)
        event_type = transition_fn(state)

        # Generate event
        seq_num = self.event_repo.get_next_sequence_number(session_id)
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            sequence_number=seq_num,
            payload=payload,
            state_version=state.state_version
        )

        self.event_repo.save(event)
        self.session_repo.save_state(state)
        return state

    def start_simulation(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        return self._execute_transition(
            session_id=session_id,
            transition_fn=StateMachine.start_simulation,
            payload={"action": "start_simulation"},
            user_id=user_id
        )

    def pause_simulation(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        return self._execute_transition(
            session_id=session_id,
            transition_fn=StateMachine.pause_simulation,
            payload={"action": "pause_simulation"},
            user_id=user_id
        )

    def resume_simulation(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        return self._execute_transition(
            session_id=session_id,
            transition_fn=StateMachine.resume_simulation,
            payload={"action": "resume_simulation"},
            user_id=user_id
        )

    def restart_simulation(self, session_id: str, user_id: Optional[str] = None) -> SessionState:
        return self._execute_transition(
            session_id=session_id,
            transition_fn=StateMachine.restart_simulation,
            payload={"action": "restart_simulation"},
            user_id=user_id
        )
