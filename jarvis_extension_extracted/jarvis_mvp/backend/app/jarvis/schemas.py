from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field

class Intent(str, Enum):
    EXPLAIN='EXPLAIN'; START_SIMULATION='START_SIMULATION'; MODIFY_SIMULATION='MODIFY_SIMULATION'; ASK_QUESTION='ASK_QUESTION'; PAUSE='PAUSE'; STOP='STOP'; RESUME='RESUME'; RESTART='RESTART'; COMPARE='COMPARE'; FAILURE_INJECTION='FAILURE_INJECTION'; SCALE='SCALE'; SHOW_COMPONENT='SHOW_COMPONENT'; QUIZ='QUIZ'; UNKNOWN='UNKNOWN'

class SimulationCommand(BaseModel):
    system: str='HDFS'; operation: str
    file_size_mb: Optional[int]=Field(None, ge=1); block_size_mb: Optional[int]=Field(None, ge=1)
    replication_factor: Optional[int]=Field(None, ge=1); datanode_count: Optional[int]=Field(None, ge=1)
    reducer_count: Optional[int]=Field(None, ge=1); node_id: Optional[str]=None; scenario_id: Optional[str]=None
    workload_type: Optional[str]=None

class VisualAction(BaseModel):
    type: str; target: Optional[str]=None; text: Optional[str]=None; payload: dict[str,Any]={}

class JarvisRequest(BaseModel):
    session_id: str; user_id: str; message: str

class JarvisResponse(BaseModel):
    session_id: str; intent: Intent; text: str
    command: Optional[SimulationCommand]=None; visual_actions: list[VisualAction]=[]
    should_speak: bool=True; should_pause: bool=False; should_resume: bool=False
    simulation_result: Optional[dict[str,Any]]=None; sources: list[str]=[]
