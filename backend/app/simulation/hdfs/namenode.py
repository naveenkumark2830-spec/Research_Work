from pydantic import BaseModel, Field
from app.simulation.common.identifiers import DeterministicIdGenerator
from app.simulation.hdfs.metadata import NameNodeMetadata


class NameNode(BaseModel):
    """NameNode model maintaining logical metadata for the HDFS cluster."""

    node_id: str = Field(default_factory=DeterministicIdGenerator.namenode_id)
    status: str = "ACTIVE"
    metadata: NameNodeMetadata = Field(default_factory=NameNodeMetadata)
