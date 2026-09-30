from abc import ABC, abstractmethod
import json
from typing import Optional, List
from sqlalchemy.orm import Session as DBSession
from app.models.checkpoint import Checkpoint
from app.db.models import CheckpointModel


class ICheckpointRepository(ABC):
    @abstractmethod
    def save(self, checkpoint: Checkpoint) -> Checkpoint:
        pass

    @abstractmethod
    def get_by_id(self, checkpoint_id: str) -> Optional[Checkpoint]:
        pass

    @abstractmethod
    def get_by_session(self, session_id: str) -> List[Checkpoint]:
        pass


class SQLAlchemyCheckpointRepository(ICheckpointRepository):
    def __init__(self, db: DBSession):
        self.db = db

    def save(self, checkpoint: Checkpoint) -> Checkpoint:
        db_checkpoint = CheckpointModel(
            checkpoint_id=checkpoint.checkpoint_id,
            session_id=checkpoint.session_id,
            created_at=checkpoint.created_at,
            sequence_number=checkpoint.sequence_number,
            state_snapshot_json=json.dumps(checkpoint.state_snapshot),
            description=checkpoint.description
        )
        self.db.add(db_checkpoint)
        self.db.commit()
        return checkpoint

    def get_by_id(self, checkpoint_id: str) -> Optional[Checkpoint]:
        db_checkpoint = self.db.query(CheckpointModel).filter(CheckpointModel.checkpoint_id == checkpoint_id).first()
        if not db_checkpoint:
            return None
        return Checkpoint(
            checkpoint_id=db_checkpoint.checkpoint_id,
            session_id=db_checkpoint.session_id,
            created_at=db_checkpoint.created_at,
            sequence_number=db_checkpoint.sequence_number,
            state_snapshot=json.loads(db_checkpoint.state_snapshot_json),
            description=db_checkpoint.description
        )

    def get_by_session(self, session_id: str) -> List[Checkpoint]:
        db_checkpoints = (
            self.db.query(CheckpointModel)
            .filter(CheckpointModel.session_id == session_id)
            .order_by(CheckpointModel.created_at.desc())
            .all()
        )
        return [
            Checkpoint(
                checkpoint_id=c.checkpoint_id,
                session_id=c.session_id,
                created_at=c.created_at,
                sequence_number=c.sequence_number,
                state_snapshot=json.loads(c.state_snapshot_json),
                description=c.description
            )
            for c in db_checkpoints
        ]
