from typing import List
from pydantic import BaseModel, Field
from app.simulation.common.enums import DataNodeStatus, HeartbeatStatus


class DataNode(BaseModel):
    node_id: str
    hostname: str
    status: DataNodeStatus = DataNodeStatus.LIVE
    capacity_bytes: int = 107374182400  # 100 GB
    used_bytes: int = 0
    available_bytes: int = 107374182400
    blocks: List[str] = Field(default_factory=list)
    heartbeat_status: HeartbeatStatus = HeartbeatStatus.HEALTHY
    last_heartbeat: float = 0.0

    def can_serve(self) -> bool:
        """Returns True if the DataNode is LIVE and healthy."""
        return self.status == DataNodeStatus.LIVE
