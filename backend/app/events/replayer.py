from typing import Optional, List
from app.state.session_state import SessionState
from app.models.event import Event
from app.core.exceptions import ResourceNotFoundError, UserIsolationError
from app.repositories.session_repository import ISessionRepository
from app.repositories.event_repository import IEventRepository
from app.repositories.checkpoint_repository import ICheckpointRepository
from app.events.applier import EventApplier


class EventReplayer:
    """Reconstructs historical SessionState from event streams without mutating live state."""

    def __init__(
        self,
        session_repo: ISessionRepository,
        event_repo: IEventRepository,
        checkpoint_repo: ICheckpointRepository
    ):
        self.session_repo = session_repo
        self.event_repo = event_repo
        self.checkpoint_repo = checkpoint_repo

    def replay_events(
        self,
        session_id: str,
        target_sequence: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> SessionState:
        """
        Reconstructs SessionState from sequence 1 up to target_sequence.
        Returns read-only replay state. Live session state is NOT mutated.
        """
        live_state = self.session_repo.get_state(session_id)
        if not live_state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and live_state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        all_events = self.event_repo.get_by_session(session_id)
        if not all_events:
            return live_state

        if target_sequence is not None:
            filtered_events = [e for e in all_events if e.sequence_number <= target_sequence]
        else:
            filtered_events = all_events

        # Initialize base initial state for replay
        first_evt = all_events[0]
        replayed_state = SessionState(
            user=live_state.user,
            session=live_state.session.model_copy(deep=True),
            state_version=1
        )

        # Incrementally apply event stream
        for evt in filtered_events:
            replayed_state = EventApplier.apply_event(replayed_state, evt)

        return replayed_state

    def replay_from_checkpoint(
        self,
        session_id: str,
        checkpoint_id: str,
        target_sequence: Optional[int] = None,
        user_id: Optional[str] = None
    ) -> SessionState:
        """
        Restores state snapshot from checkpoint at sequence M and replays events M+1 ... N.
        """
        live_state = self.session_repo.get_state(session_id)
        if not live_state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and live_state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        checkpoint = self.checkpoint_repo.get_by_id(checkpoint_id)
        if not checkpoint or checkpoint.session_id != session_id:
            raise ResourceNotFoundError("Checkpoint", checkpoint_id)

        # Restore snapshot state
        checkpoint_state = SessionState.model_validate(checkpoint.state_snapshot)
        chk_seq = checkpoint.sequence_number

        # Fetch events occurring after checkpoint sequence
        subsequent_events = self.event_repo.get_by_sequence_range(
            session_id,
            start_seq=chk_seq + 1,
            end_seq=target_sequence or 99999999
        )

        replayed_state = checkpoint_state.model_copy(deep=True)
        for evt in subsequent_events:
            replayed_state = EventApplier.apply_event(replayed_state, evt)

        return replayed_state
