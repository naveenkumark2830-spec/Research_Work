from typing import Dict, List, Set, Optional
from pydantic import BaseModel, Field
from app.simulation.hdfs.file import HDFSFile
from app.simulation.hdfs.block import HDFSBlock


class NameNodeMetadata(BaseModel):
    """Logical NameNode metadata store (stores zero file payload data)."""

    files: Dict[str, HDFSFile] = Field(default_factory=dict)         # path -> HDFSFile
    file_by_id: Dict[str, HDFSFile] = Field(default_factory=dict)    # file_id -> HDFSFile
    blocks: Dict[str, HDFSBlock] = Field(default_factory=dict)       # block_id -> HDFSBlock
    under_replicated_blocks: Set[str] = Field(default_factory=set)
    lost_blocks: Set[str] = Field(default_factory=set)

    def register_file(self, hdfs_file: HDFSFile) -> None:
        self.files[hdfs_file.path] = hdfs_file
        self.file_by_id[hdfs_file.file_id] = hdfs_file

    def register_block(self, block: HDFSBlock) -> None:
        self.blocks[block.block_id] = block

    def get_file(self, path: str) -> Optional[HDFSFile]:
        return self.files.get(path)

    def get_block(self, block_id: str) -> Optional[HDFSBlock]:
        return self.blocks.get(block_id)

    def get_block_locations(self, block_id: str) -> List[str]:
        block = self.blocks.get(block_id)
        if not block:
            return []
        return list(block.replica_nodes)

    def get_file_blocks(self, file_id: str) -> List[HDFSBlock]:
        hdfs_file = self.file_by_id.get(file_id)
        if not hdfs_file:
            return []
        return [self.blocks[b_id] for b_id in hdfs_file.block_ids if b_id in self.blocks]
