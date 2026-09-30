from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from .intent import IntentType


class ActionType(str, Enum):
    """Enumeration of structured actions executable by existing backend services."""

    UPDATE_CONFIG = "UPDATE_CONFIG"
    START_SIMULATION = "START_SIMULATION"
    PAUSE_SIMULATION = "PAUSE_SIMULATION"
    RESUME_SIMULATION = "RESUME_SIMULATION"
    RESTART_SIMULATION = "RESTART_SIMULATION"
    SET_SPEED = "SET_SPEED"
    ADD_DATANODE = "ADD_DATANODE"
    REMOVE_DATANODE = "REMOVE_DATANODE"
    KILL_DATANODE = "KILL_DATANODE"
    RECOVER_DATANODE = "RECOVER_DATANODE"
    SHOW_COMPONENT = "SHOW_COMPONENT"
    EXPLAIN_COMPONENT = "EXPLAIN_COMPONENT"
    ASK_HADOOP_QUESTION = "ASK_HADOOP_QUESTION"
    COMPARE_CONFIGURATIONS = "COMPARE_CONFIGURATIONS"
    NO_OP = "NO_OP"


@dataclass
class Action:
    type: ActionType | Any = None
    intent: IntentType | None = None
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntentResult:
    intent: IntentType
    confidence: float = 1.0
    parameters: dict[str, Any] = field(default_factory=dict)
    explanation: str | None = None
    action: Optional[Action] = None
    response: str | None = None
    requires_confirmation: bool = False
    clarification_question: str | None = None
