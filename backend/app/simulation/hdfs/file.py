from typing import List
from pydantic import BaseModel, Field
from app.simulation.common.enums import FileStatus


class HDFSFile(BaseModel):
    file_id: str
    path: str
    size_bytes: int
    block_size_bytes: int
    block_ids: List[str] = Field(default_factory=list)
    replication_factor: int = 3
    status: FileStatus = FileStatus.WRITING
