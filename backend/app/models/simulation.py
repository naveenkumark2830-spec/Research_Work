from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class SimulationSystem(str, Enum):
    HDFS = "HDFS"
    MAPREDUCE = "MAPREDUCE"
    YARN = "YARN"
    HADOOP_1 = "HADOOP_1"
    HADOOP_2 = "HADOOP_2"


class SimulationStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SimulationStage(str, Enum):
    INITIALIZATION = "INITIALIZATION"
    INPUT = "INPUT"
    BLOCK_CREATION = "BLOCK_CREATION"
    REPLICATION = "REPLICATION"
    MAP = "MAP"
    SHUFFLE = "SHUFFLE"
    REDUCE = "REDUCE"
    OUTPUT = "OUTPUT"
    FAILURE = "FAILURE"
    RECOVERY = "RECOVERY"


class SimulationConfig(BaseModel):
    file_size_mb: int = Field(default=500, ge=1, le=10240)
    block_size_mb: int = Field(default=128, ge=1, le=1024)
    replication_factor: int = Field(default=3, ge=1, le=10)
    datanode_count: int = Field(default=5, ge=1, le=50)
    reducer_count: int = Field(default=5, ge=1, le=100)
    simulation_speed: float = Field(default=1.0, ge=0.1, le=10.0)
    file_size: Optional[int] = 524288000
    block_size: Optional[int] = 134217728
    data_node_count: Optional[int] = 5
    custom_parameters: Dict[str, Any] = Field(default_factory=dict)

    @field_validator('replication_factor')
    def validate_replication(cls, v, info):
        return v


class SimulationState(BaseModel):
    system: SimulationSystem = SimulationSystem.HDFS
    scenario_id: Optional[str] = "default_hdfs_write"
    status: SimulationStatus = SimulationStatus.IDLE
    current_stage: SimulationStage = SimulationStage.INITIALIZATION
    progress: float = 0.0
    started_at: Optional[datetime] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    simulation_time: float = 0.0
    configuration: SimulationConfig = Field(default_factory=SimulationConfig)
