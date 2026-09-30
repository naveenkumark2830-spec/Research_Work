from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class VisualizationStatus(str, Enum):
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"


class VisualizationState(BaseModel):
    status: VisualizationStatus = VisualizationStatus.IDLE
    active_component: Optional[str] = "NameNode"
    selected_component: Optional[str] = None
    selected_block: Optional[str] = None
    active_nodes: List[str] = Field(default_factory=lambda: ["DataNode_1", "DataNode_2", "DataNode_3"])
    highlighted_nodes: List[str] = Field(default_factory=list)
    current_animation: Optional[str] = None
    animation_progress: float = 0.0
    camera_state: Dict[str, Any] = Field(default_factory=lambda: {"zoom": 1.0, "position": [0, 0, 0]})
    viewport_state: Dict[str, Any] = Field(default_factory=lambda: {"width": 1920, "height": 1080})
