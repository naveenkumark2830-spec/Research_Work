import uuid
from datetime import datetime, timezone
from typing import List, Optional
from app.models.checkpoint import Checkpoint
from app.models.event import Event, EventType
from app.state.session_state import SessionState
from app.core.exceptions import ResourceNotFoundError, UserIsolationError
from app.repositories.session_repository import ISessionRepository
from app.repositories.checkpoint_repository import ICheckpointRepository
from app.repositories.event_repository import IEventRepository


class CheckpointService:
    def __init__(
        self,
        session_repo: ISessionRepository,
        checkpoint_repo: ICheckpointRepository,
        event_repo: IEventRepository
    ):
        self.session_repo = session_repo
        self.checkpoint_repo = checkpoint_repo
        self.event_repo = event_repo

    def create_checkpoint(
        self,
        session_id: str,
        description: str = "User Checkpoint",
        user_id: Optional[str] = None
    ) -> Checkpoint:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        now = datetime.now(timezone.utc)
        checkpoint_id = f"chk_{uuid.uuid4().hex[:12]}"
        seq_num = self.event_repo.get_next_sequence_number(session_id)

        # Snapshot exact state
        snapshot = state.model_dump(mode="json")

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            session_id=session_id,
            created_at=now,
            sequence_number=seq_num,
            state_snapshot=snapshot,
            description=description
        )

        self.checkpoint_repo.save(checkpoint)

        # Log CHECKPOINT_CREATED event
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            event_type=EventType.CHECKPOINT_CREATED,
            timestamp=now,
            sequence_number=seq_num,
            payload={"checkpoint_id": checkpoint_id, "description": description},
            state_version=state.state_version
        )
        self.event_repo.save(event)

        return checkpoint

    def get_checkpoints(self, session_id: str, user_id: Optional[str] = None) -> List[Checkpoint]:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)
        return self.checkpoint_repo.get_by_session(session_id)

    def restore_checkpoint(
        self,
        session_id: str,
        checkpoint_id: str,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        checkpoint = self.checkpoint_repo.get_by_id(checkpoint_id)
        if not checkpoint or checkpoint.session_id != session_id:
            raise ResourceNotFoundError("Checkpoint", checkpoint_id)

        # Reconstruct state from checkpoint snapshot
        restored_state = SessionState.model_validate(checkpoint.state_snapshot)

        now = datetime.now(timezone.utc)
        # Monotonically increment state_version to indicate new state version after restore
        restored_state.state_version = state.state_version + 1
        restored_state.session.updated_at = now
        restored_state.session.last_activity_at = now

        self.session_repo.save_state(restored_state)

        # Log STATE_RESTORED event
        seq_num = self.event_repo.get_next_sequence_number(session_id)
        event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            event_type=EventType.STATE_RESTORED,
            timestamp=now,
            sequence_number=seq_num,
            payload={"checkpoint_id": checkpoint_id, "restored_to_sequence": checkpoint.sequence_number},
            state_version=restored_state.state_version
        )
        self.event_repo.save(event)

        return restored_state
