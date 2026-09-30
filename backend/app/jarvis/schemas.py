from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional, List, Dict

from pydantic import BaseModel, Field, model_validator


class VisualizationStep(BaseModel):
    type: Literal[
        "show_cluster",
        "show_file",
        "create_blocks",
        "replicate_blocks",
        "show_namenode",
        "show_datanodes",
        "highlight_block",
        "show_pipeline",
        "show_failure",
        "show_recovery",
        "explain",
    ]

    title: str
    description: str
    data: dict[str, Any] = Field(default_factory=dict)
    duration_ms: int = 1200


class SimulationAction(BaseModel):
    action: Literal[
        "none",
        "create_cluster",
        "write_file",
        "kill_datanode",
        "recover_datanode",
        "recover_under_replicated_blocks",
    ] = "none"

    parameters: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_action(self):
        action = self.action
        params = self.parameters

        if action == "none":
            return self

        if action == "create_cluster":
            return self

        if action == "write_file":
            path = params.get("path")
            size_bytes = params.get("size_bytes")
            size = params.get("size")

            if not isinstance(path, str) or not path.strip():
                raise ValueError("write_file requires a valid path")

            if size_bytes is not None:
                if not isinstance(size_bytes, int) or size_bytes <= 0:
                    raise ValueError(
                        "write_file requires positive integer size_bytes"
                    )
            elif size is not None:
                try:
                    num_val = float(size)
                    if num_val <= 0:
                        raise ValueError("write_file requires positive size")
                except (TypeError, ValueError):
                    raise ValueError("write_file requires numeric size")
            else:
                raise ValueError(
                    "write_file requires positive integer size_bytes"
                )

            return self

        if action in {"kill_datanode", "recover_datanode"}:
            node_id = params.get("node_id")

            if not isinstance(node_id, str) or not node_id.strip():
                raise ValueError(
                    f"{action} requires node_id"
                )

            return self

        if action == "recover_under_replicated_blocks":
            return self

        raise ValueError(f"Unsupported simulation action: {action}")


class TeddyPlan(BaseModel):
    intent: str

    answer: str

    voice_text: str

    simulation_required: bool = False

    simulation_action: SimulationAction = Field(
        default_factory=lambda: SimulationAction(action="none")
    )

    visualization: list[VisualizationStep] = Field(
        default_factory=list
    )

    sources: list[str] = Field(default_factory=list)


class TeddyRequest(BaseModel):
    session_id: str
    user_id: str | None = None
    message: str


class TeddyResponse(BaseModel):
    session_id: str
    user_message: str
    plan: TeddyPlan
    simulation_state: dict[str, Any] | None = None
    visualization_scene: dict[str, Any] | None = None


# Legacy compatibility schema definitions
class Intent(str, Enum):
    EXPLAIN = 'EXPLAIN'
    START_SIMULATION = 'START_SIMULATION'
    MODIFY_SIMULATION = 'MODIFY_SIMULATION'
    ASK_QUESTION = 'ASK_QUESTION'
    PAUSE = 'PAUSE'
    STOP = 'STOP'
    RESUME = 'RESUME'
    RESTART = 'RESTART'
    COMPARE = 'COMPARE'
    FAILURE_INJECTION = 'FAILURE_INJECTION'
    SCALE = 'SCALE'
    SHOW_COMPONENT = 'SHOW_COMPONENT'
    QUIZ = 'QUIZ'
    UNKNOWN = 'UNKNOWN'


class SimulationCommand(BaseModel):
    system: str = 'HDFS'
    operation: str
    file_size_mb: Optional[int] = Field(None, ge=1)
    block_size_mb: Optional[int] = Field(None, ge=1)
    replication_factor: Optional[int] = Field(None, ge=1)
    datanode_count: Optional[int] = Field(None, ge=1)
    reducer_count: Optional[int] = Field(None, ge=1)
    node_id: Optional[str] = None
    scenario_id: Optional[str] = None
    workload_type: Optional[str] = None


class VisualAction(BaseModel):
    type: str
    target: Optional[str] = None
    text: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class JarvisRequest(BaseModel):
    session_id: str
    user_id: str
    message: str


class JarvisResponse(BaseModel):
    session_id: str
    intent: Intent
    text: str
    command: Optional[SimulationCommand] = None
    visual_actions: List[VisualAction] = Field(default_factory=list)
    should_speak: bool = True
    should_pause: bool = False
    should_resume: bool = False
    simulation_result: Optional[Dict[str, Any]] = None
    sources: List[str] = Field(default_factory=list)
