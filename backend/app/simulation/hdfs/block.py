import math
from typing import List
from pydantic import BaseModel, Field
from app.simulation.common.enums import BlockState


def calculate_block_count(file_size_bytes: int, block_size_bytes: int) -> int:
    """Calculates ceil(file_size / block_size) using integer division math."""
    if file_size_bytes <= 0 or block_size_bytes <= 0:
        return 0
    return math.ceil(file_size_bytes / block_size_bytes)


class HDFSBlock(BaseModel):
    block_id: str
    file_id: str
    index: int
    size_bytes: int
    replica_nodes: List[str] = Field(default_factory=list)
    desired_replication: int = 3
    state: BlockState = BlockState.CREATED

    @property
    def healthy_replica_count(self) -> int:
        return len(set(self.replica_nodes))
