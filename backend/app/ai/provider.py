from __future__ import annotations

import re
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from app.ai.intent import IntentType
from app.ai.action import ActionType, Action, IntentResult
from app.ai.context import AIContext
from app.core.config import settings

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Level 4 LLM Provider Interface & Data Models
# ------------------------------------------------------------------

@dataclass(frozen=True)
class LLMRequest:
    prompt: str
    system_prompt: str | None = None
    temperature: float = 0.2
    max_tokens: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    fallback_used: bool = False


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        raise NotImplementedError


# ------------------------------------------------------------------
# Legacy / Orchestrator AIProvider & Rule-Based Mock Provider
# ------------------------------------------------------------------

class AIProvider(ABC):
    """Abstract interface for AI natural-language orchestrators."""

    @abstractmethod
    def generate_structured_response(self, context: AIContext) -> IntentResult:
        pass


class MockAIProvider(AIProvider):
    """
    Deterministic rule-based NLP provider for offline testing & execution.
    Parses natural language expressions into strongly typed IntentResult actions.
    """

    def generate_structured_response(self, context: AIContext) -> IntentResult:
        msg = context.user_message.strip().lower().rstrip('.!?')
        viz = context.visualization_state or {}
        sim_state = context.simulation_state or {}
        events = (context.event_context or {}).get("recent_events", [])
        recent_msgs = (context.conversation_context or {}).get("recent_messages", [])

        # -------------------------------------------------------------
        # 1. Ambiguous Prompt Detection
        # -------------------------------------------------------------
        if msg in ["make it bigger", "increase it", "make it larger"]:
            return IntentResult(
                intent=IntentType.MODIFY_SIMULATION,
                action=Action(type=ActionType.NO_OP),
                response="What would you like to increase — file size, block size, or the number of DataNodes?",
                clarification_question="What would you like to increase — file size, block size, or the number of DataNodes?"
            )
        if msg in ["use more replicas", "increase replication", "more copies"]:
            return IntentResult(
                intent=IntentType.MODIFY_SIMULATION,
                action=Action(type=ActionType.NO_OP),
                response="What replication factor would you like?",
                clarification_question="What replication factor would you like?"
            )
        if msg in ["kill a datanode", "fail a datanode", "kill datanode"]:
            return IntentResult(
                intent=IntentType.FAILURE_INJECTION,
                action=Action(type=ActionType.NO_OP),
                response="Which DataNode would you like to kill?",
                clarification_question="Which DataNode would you like to kill?"
            )

        # -------------------------------------------------------------
        # 2. Simulation Lifecycle Controls (Start, Pause, Resume, Stop, Restart)
        # -------------------------------------------------------------
        if any(term in msg for term in ["jarvis, stop", "stop simulation", "stop"]):
            return IntentResult(
                intent=IntentType.STOP,
                action=Action(type=ActionType.PAUSE_SIMULATION),
                response="Stopping the simulation."
            )
        if any(term in msg for term in ["restart the simulation", "restart simulation", "start again", "restart"]):
            return IntentResult(
                intent=IntentType.RESTART,
                action=Action(type=ActionType.RESTART_SIMULATION),
                response="Restarting HDFS simulation from clean initialization state."
            )
        if any(term in msg for term in ["start the hdfs simulation", "start the simulation", "run the hdfs write", "start simulation", "start"]):
            return IntentResult(
                intent=IntentType.START_SIMULATION,
                action=Action(type=ActionType.START_SIMULATION),
                response="Starting HDFS write simulation."
            )
        if msg in ["pause", "pause simulation"]:
            return IntentResult(
                intent=IntentType.PAUSE,
                action=Action(type=ActionType.PAUSE_SIMULATION),
                response="Simulation paused."
            )
        if any(term in msg for term in ["continue", "resume", "resume simulation"]):
            return IntentResult(
                intent=IntentType.RESUME,
                action=Action(type=ActionType.RESUME_SIMULATION),
                response="Resuming simulation execution."
            )

        # -------------------------------------------------------------
        # 3. DataNode Action Parsing (Kill, Recover, Add, Remove)
        # -------------------------------------------------------------
        # Kill / Fail DataNode
        kill_match = re.search(r"(?:kill|fail|take|bring)\s+(?:datanode|dn)[-\s]*(\d+)(?:\s+down)?", msg)
        if kill_match and not re.search(r"(?:back|recover|up)", msg):
            dn_num = kill_match.group(1)
            dn_id = f"datanode-{dn_num}"
            return IntentResult(
                intent=IntentType.FAILURE_INJECTION,
                action=Action(type=ActionType.KILL_DATANODE, parameters={"datanode_id": dn_id}),
                response=f"Injecting failure into DataNode-{dn_num}."
            )

        # Recover DataNode
        recover_match = re.search(r"(?:recover|bring|restore)\s+(?:datanode|dn)[-\s]*(\d+)(?:\s+back|\s+up)?", msg)
        if recover_match:
            dn_num = recover_match.group(1)
            dn_id = f"datanode-{dn_num}"
            return IntentResult(
                intent=IntentType.FAILURE_INJECTION,
                action=Action(type=ActionType.RECOVER_DATANODE, parameters={"datanode_id": dn_id}),
                response=f"Recovering DataNode-{dn_num}."
            )

        # Add DataNode(s)
        add_match = re.search(r"add\s+(a|one|two|three|four|five|\d+)?\s*(?:datanode|dn)s?", msg)
        if add_match:
            raw_count = add_match.group(1)
            count_map = {"a": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
            count = count_map.get(raw_count, int(raw_count) if raw_count and raw_count.isdigit() else 1)
            return IntentResult(
                intent=IntentType.SCALE,
                action=Action(type=ActionType.ADD_DATANODE, parameters={"count": count}),
                response=f"Adding {count} DataNode(s) to the cluster."
            )

        # Remove DataNode
        rem_match = re.search(r"remove\s+(?:datanode|dn)[-\s]*(\d+)", msg)
        if rem_match:
            dn_num = rem_match.group(1)
            dn_id = f"datanode-{dn_num}"
            return IntentResult(
                intent=IntentType.SCALE,
                action=Action(type=ActionType.REMOVE_DATANODE, parameters={"datanode_id": dn_id}),
                response=f"Removing DataNode-{dn_num} from cluster."
            )

        # -------------------------------------------------------------
        # 4. Simulation Speed Control Parsing
        # -------------------------------------------------------------
        speed_match = re.search(r"set\s+speed\s+to\s+([0-9.]+)\s*x?", msg)
        if speed_match:
            speed_val = float(speed_match.group(1))
            return IntentResult(
                intent=IntentType.MODIFY_SIMULATION,
                action=Action(type=ActionType.SET_SPEED, parameters={"speed": speed_val}),
                response=f"Simulation speed updated to {speed_val}x."
            )

        # -------------------------------------------------------------
        # 5. Parameter Configuration Updates (UPDATE_CONFIG)
        # -------------------------------------------------------------
        config_params = {}

        # Multi-parameter extraction check
        # e.g., "Create a 500 MB file with 128 MB blocks and 3 replicas"
        file_match = re.search(r"(\d+)\s*(?:mb|gb)?\s*file", msg)
        if not file_match:
            file_match = re.search(r"(?:file\s+size|file)\s*(?:to|=)?\s*(\d+)\s*(mb|gb)?", msg)
        if file_match:
            val = int(file_match.group(1))
            unit = (file_match.group(2) or "").lower()
            if unit == "gb" or val <= 10:
                val *= 1024
            config_params["file_size_mb"] = val

        block_match = re.search(r"(\d+)\s*mb\s*blocks?", msg)
        if not block_match:
            block_match = re.search(r"block\s+size\s*(?:to|=)?\s*(\d+)", msg)
        if block_match:
            config_params["block_size_mb"] = int(block_match.group(1))

        repl_match = re.search(r"(?:replication|replicas?|rf)\s*(?:factor|to|=)?\s*(\d+)", msg)
        if not repl_match:
            repl_match = re.search(r"(\d+)\s*replicas", msg)
        if repl_match:
            config_params["replication_factor"] = int(repl_match.group(1))

        dn_count_match = re.search(r"(\d+)\s*datanodes?", msg)
        if dn_count_match and not re.search(r"(?:kill|remove|add)", msg):
            config_params["datanode_count"] = int(dn_count_match.group(1))

        red_count_match = re.search(r"(\d+)\s*reducers?", msg)
        if red_count_match:
            config_params["reducer_count"] = int(red_count_match.group(1))

        if config_params:
            resp_str = ", ".join([f"{k}={v}" for k, v in config_params.items()])
            return IntentResult(
                intent=IntentType.MODIFY_SIMULATION,
                action=Action(type=ActionType.UPDATE_CONFIG, parameters=config_params),
                response=f"Updating simulation configuration parameters: {resp_str}."
            )

        # -------------------------------------------------------------
        # 6. Explanations, Visual Context & Contextual Follow-ups
        # -------------------------------------------------------------
        # Check visual selection context ("Why is this red?", "Explain this")
        sel_comp = viz.get("selected_component") or viz.get("selected_component_id")
        sel_type = viz.get("selected_component_type")
        if "this" in msg or "selected" in msg or msg in ["explain this", "what is this", "why is this red?"]:
            if sel_comp:
                datanodes = sim_state.get("datanodes", {})
                comp_info = datanodes.get(sel_comp, {})
                status = comp_info.get("status", "UNKNOWN")
                if status == "FAILED" or "red" in msg:
                    explanation = f"{sel_comp} is currently FAILED (shown in red) due to a simulated hardware/network crash."
                else:
                    explanation = f"{sel_comp} is an active DataNode in status {status} hosting HDFS block replicas."
                return IntentResult(
                    intent=IntentType.EXPLAIN,
                    action=Action(type=ActionType.EXPLAIN_COMPONENT, parameters={"component_id": sel_comp}),
                    response=explanation
                )

        if any(term in msg for term in ["under-replicated", "yellow", "blocks yellow"]):
            return IntentResult(
                intent=IntentType.EXPLAIN,
                action=Action(type=ActionType.ASK_HADOOP_QUESTION),
                response="Blocks become under-replicated (yellow) when a hosting DataNode fails or is removed, leaving fewer healthy replicas than the desired replication factor."
            )

        if "namenode" in msg:
            return IntentResult(
                intent=IntentType.EXPLAIN,
                action=Action(type=ActionType.ASK_HADOOP_QUESTION),
                response="The NameNode is the master node in HDFS. It manages the file system namespace, maintains block metadata, and directs DataNodes."
            )

        if "datanode" in msg and ("explain" in msg or "what" in msg):
            return IntentResult(
                intent=IntentType.EXPLAIN,
                action=Action(type=ActionType.ASK_HADOOP_QUESTION),
                response="DataNodes are worker nodes in HDFS that store and serve data blocks as directed by the NameNode."
            )

        if "why do we need replication" in msg or ("replication" in msg and "why" in msg):
            return IntentResult(
                intent=IntentType.EXPLAIN,
                action=Action(type=ActionType.ASK_HADOOP_QUESTION),
                response="Replication ensures high availability and fault tolerance. If a DataNode crashes, data remains accessible from alternate replicas."
            )

        if "what just happened" in msg or "why?" in msg or "how?" in msg:
            if events:
                last_evt = events[-1]
                evt_type = last_evt.get("event_type") or last_evt.get("sim_event_type")
                return IntentResult(
                    intent=IntentType.EXPLAIN,
                    action=Action(type=ActionType.ASK_HADOOP_QUESTION),
                    response=f"The last simulation event was '{evt_type}'. State sequence is currently at #{last_evt.get('sequence_number', 0)}."
                )
            return IntentResult(
                intent=IntentType.EXPLAIN,
                action=Action(type=ActionType.ASK_HADOOP_QUESTION),
                response="The simulation is idle in its current lifecycle state."
            )

        # Default fallback / general answer
        return IntentResult(
            intent=IntentType.ASK_QUESTION,
            action=Action(type=ActionType.ASK_HADOOP_QUESTION),
            response=f"I understand your question regarding '{context.user_message}'. I am ready to assist with HDFS simulation and architecture."
        )


def get_ai_provider() -> AIProvider:
    """Factory function returning configured AIProvider based on environment settings."""
    provider_name = (getattr(settings, "JARVIS_LLM_PROVIDER", None) or settings.AI_PROVIDER or "mock").lower()
    gemini_key = getattr(settings, "GEMINI_API_KEY", None) or os.getenv("GEMINI_API_KEY")

    if provider_name == "gemini" and gemini_key:
        try:
            from app.jarvis.provider import GeminiAIProvider
            provider = GeminiAIProvider(api_key=gemini_key)
            if provider.client:
                return provider
        except Exception as e:
            logger.warning(f"Falling back to MockAIProvider: {e}")

    return MockAIProvider()
