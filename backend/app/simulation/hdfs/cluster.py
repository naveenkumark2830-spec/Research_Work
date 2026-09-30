from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, model_validator
from app.models.simulation import SimulationStatus, SimulationStage
from app.simulation.common.exceptions import InvalidClusterConfigurationError
from app.simulation.common.identifiers import DeterministicIdGenerator
from app.simulation.hdfs.namenode import NameNode
from app.simulation.hdfs.datanode import DataNode
from app.simulation.hdfs.file import HDFSFile
from app.simulation.hdfs.block import HDFSBlock


class HDFSClusterConfig(BaseModel):
    file_size_mb: int = 500
    block_size_mb: int = 128
    replication_factor: int = 3
    data_node_count: int = 5
    reducer_count: int = 5
    simulation_speed: float = 1.0
    file_size_bytes: int = 524288000           # e.g., 500 MB
    block_size_bytes: int = 134217728          # e.g., 128 MB
    data_node_capacity_bytes: int = 107374182400  # 100 GB
    rack_count: int = 1
    rack_aware: bool = False
    heartbeat_interval: float = 3.0
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_cluster_config(self):
        if self.file_size_mb < 1 or self.file_size_mb > 10240:
            raise InvalidClusterConfigurationError("file_size_mb must be between 1 and 10240")
        if self.block_size_mb < 1 or self.block_size_mb > 1024:
            raise InvalidClusterConfigurationError("block_size_mb must be between 1 and 1024")
        if self.replication_factor < 1 or self.replication_factor > 10:
            raise InvalidClusterConfigurationError("replication_factor must be between 1 and 10")
        if self.data_node_count < 1 or self.data_node_count > 50:
            raise InvalidClusterConfigurationError("data_node_count must be between 1 and 50")
        if self.reducer_count < 1 or self.reducer_count > 100:
            raise InvalidClusterConfigurationError("reducer_count must be between 1 and 100")
        if self.simulation_speed < 0.1 or self.simulation_speed > 10.0:
            raise InvalidClusterConfigurationError("simulation_speed must be between 0.1 and 10.0")

        if self.replication_factor > self.data_node_count:
            raise InvalidClusterConfigurationError(
                f"Replication factor {self.replication_factor} cannot exceed {self.data_node_count} available DataNodes."
            )

        # Sync bytes representations
        self.file_size_bytes = self.file_size_mb * 1024 * 1024
        self.block_size_bytes = self.block_size_mb * 1024 * 1024
        return self


class HDFSClusterState(BaseModel):
    cluster_id: str = Field(default_factory=DeterministicIdGenerator.cluster_id)
    configuration: HDFSClusterConfig = Field(default_factory=HDFSClusterConfig)
    namenode: NameNode = Field(default_factory=NameNode)
    datanodes: Dict[str, DataNode] = Field(default_factory=dict)
    files: Dict[str, HDFSFile] = Field(default_factory=dict)
    blocks: Dict[str, HDFSBlock] = Field(default_factory=dict)
    current_stage: SimulationStage = SimulationStage.INITIALIZATION
    status: SimulationStatus = SimulationStatus.IDLE
    simulation_time: float = 0.0
    state_version: int = 1
