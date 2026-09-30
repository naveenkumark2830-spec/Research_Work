import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.ai.intent import IntentType
from app.ai.action import ActionType, Action, IntentResult
from app.ai.context import AIContext
from app.ai.validator import ActionValidator
from app.ai.provider import get_ai_provider, AIProvider
from app.models.event import Event, EventCategory, EventType
from app.models.conversation import Message, MessageRole
from app.simulation.common.exceptions import HDFSBaseException
from app.core.exceptions import BaseAppException, ResourceNotFoundError, UserIsolationError
from app.simulation.hdfs.cluster import HDFSClusterConfig, HDFSClusterState
from app.repositories.session_repository import ISessionRepository
from app.repositories.event_repository import IEventRepository
from app.services.hdfs_service import HDFSService
from app.services.state_service import StateService

logger = logging.getLogger(__name__)


class OrchestrationResponse(BaseModel):
    """Structured response returned by AI Orchestrator API endpoint."""

    session_id: str
    intent: IntentType
    action_executed: bool
    response: str
    action: Optional[Action] = None
    clarification_question: Optional[str] = None
    error: Optional[Dict[str, Any]] = None
    simulation_state: Dict[str, Any] = Field(default_factory=dict)
    visualization_state: Dict[str, Any] = Field(default_factory=dict)
    event: Optional[Dict[str, Any]] = None


class AIOrchestrator:
    """Orchestrates natural language interpretation, validation, and backend service dispatch."""

    def __init__(
        self,
        session_repo: ISessionRepository,
        event_repo: IEventRepository,
        hdfs_service: HDFSService,
        state_service: StateService,
        provider: Optional[AIProvider] = None
    ):
        self.session_repo = session_repo
        self.event_repo = event_repo
        self.hdfs_service = hdfs_service
        self.state_service = state_service
        self.provider = provider or get_ai_provider()

    def process_message(
        self,
        session_id: str,
        message: str,
        user_id: Optional[str] = None,
        visualization_context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResponse:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        target_user_id = user_id or state.user.user_id

        # 1. Fetch recent events and conversation history for context
        recent_events_obj = self.event_repo.get_by_session(session_id)[-10:]
        recent_events = [e.model_dump(mode="json") for e in recent_events_obj]
        recent_messages = [m.model_dump(mode="json") for m in state.conversation.recent_messages[-10:]]

        # Get authoritative cluster state
        cluster_state = self.hdfs_service.get_hdfs_cluster_state(session_id, user_id=target_user_id)
        sim_state_dump = cluster_state.model_dump(mode="json")

        # 2. Build AI Context
        ai_context = AIContext(
            user_message=message,
            user_context={"user_id": target_user_id, "display_name": state.user.display_name},
            session_context={"session_id": session_id, "topic": state.session.current_topic},
            conversation_context={"recent_messages": recent_messages},
            simulation_state=sim_state_dump,
            visualization_state=visualization_context or {},
            event_context={
                "recent_events": recent_events,
                "current_sequence": recent_events_obj[-1].sequence_number if recent_events_obj else 0,
                "current_logical_time": cluster_state.simulation_time
            }
        )

        # 3. Obtain IntentResult from AI Provider
        intent_result: IntentResult = self.provider.generate_structured_response(ai_context)

        # 4. Action Validation & Execution Dispatch
        action_executed = False
        execution_error = None
        executed_event = None

        if intent_result.action and intent_result.action.type != ActionType.NO_OP:
            try:
                ActionValidator.validate_action(intent_result.action, sim_state_dump)
                action_executed, executed_event = self._dispatch_action(
                    session_id=session_id,
                    user_id=target_user_id,
                    action=intent_result.action,
                    current_cluster_state=cluster_state
                )
            except (HDFSBaseException, BaseAppException) as exc:
                action_executed = False
                execution_error = {
                    "code": getattr(exc, "error_code", "VALIDATION_FAILED"),
                    "message": exc.message
                }
                # Rule 25: AI response MUST reflect backend failure rather than hallucinating success
                intent_result.response = exc.message

        # 5. Re-fetch refreshed session state before appending conversation messages
        state = self.session_repo.get_state(session_id) or state

        # 6. Integrate User and Assistant Messages into Session Conversation & Event Stream
        now = datetime.now(timezone.utc)
        user_msg = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            role=MessageRole.USER,
            content=message,
            timestamp=now
        )
        assistant_msg = Message(
            message_id=f"msg_{uuid.uuid4().hex[:12]}",
            role=MessageRole.ASSISTANT,
            content=intent_result.response,
            timestamp=now
        )

        state.conversation.recent_messages.append(user_msg)
        state.conversation.recent_messages.append(assistant_msg)
        state.conversation.conversation_turn_count += 2
        state.conversation.last_user_message = message
        state.conversation.last_assistant_message = intent_result.response
        state.state_version += 1
        state.session.updated_at = now

        # Record conversation event
        seq_num = self.event_repo.get_next_sequence_number(session_id)
        conv_event = Event(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            session_id=session_id,
            category=EventCategory.SYSTEM,
            event_type=EventType.CONVERSATION_MESSAGE_ADDED,
            timestamp=now,
            sequence_number=seq_num,
            payload={
                "user_message": message,
                "assistant_message": intent_result.response,
                "intent": intent_result.intent.value,
                "action_executed": action_executed
            },
            state_version=state.state_version
        )
        self.event_repo.save(conv_event)
        self.session_repo.save_state(state)

        # 6. Fetch final refreshed state for payload
        final_cluster_state = self.hdfs_service.get_hdfs_cluster_state(session_id, user_id=target_user_id)
        final_session_state = self.session_repo.get_state(session_id)

        return OrchestrationResponse(
            session_id=session_id,
            intent=intent_result.intent,
            action_executed=action_executed,
            response=intent_result.response,
            action=intent_result.action,
            clarification_question=intent_result.clarification_question,
            error=execution_error,
            simulation_state=final_cluster_state.model_dump(mode="json"),
            visualization_state=final_session_state.visualization.model_dump(mode="json"),
            event=executed_event.model_dump(mode="json") if executed_event else None
        )

    def _dispatch_action(
        self,
        session_id: str,
        user_id: str,
        action: Action,
        current_cluster_state: HDFSClusterState
    ) -> tuple[bool, Optional[Event]]:
        params = action.parameters or {}
        a_type = action.type

        if a_type == ActionType.UPDATE_CONFIG:
            # Build merged configuration
            curr_cfg = current_cluster_state.configuration
            new_cfg = HDFSClusterConfig(
                file_size_mb=params.get("file_size_mb", curr_cfg.file_size_mb),
                block_size_mb=params.get("block_size_mb", curr_cfg.block_size_mb),
                replication_factor=params.get("replication_factor", curr_cfg.replication_factor),
                data_node_count=params.get("datanode_count", curr_cfg.data_node_count),
                reducer_count=params.get("reducer_count", curr_cfg.reducer_count),
                simulation_speed=params.get("simulation_speed", curr_cfg.simulation_speed)
            )
            self.hdfs_service.update_config(session_id, new_cfg, user_id=user_id)

        elif a_type == ActionType.START_SIMULATION:
            curr_cfg = current_cluster_state.configuration
            self.hdfs_service.write_file(
                session_id,
                path="input/data.csv",
                size_bytes=curr_cfg.file_size_bytes,
                user_id=user_id
            )

        elif a_type == ActionType.PAUSE_SIMULATION:
            self.state_service.pause_simulation(session_id, user_id=user_id)

        elif a_type == ActionType.RESUME_SIMULATION:
            self.state_service.resume_simulation(session_id, user_id=user_id)

        elif a_type == ActionType.RESTART_SIMULATION:
            self.hdfs_service.restart_simulation(session_id, user_id=user_id)

        elif a_type == ActionType.SET_SPEED:
            speed = float(params.get("speed", 1.0))
            self.hdfs_service.set_speed(session_id, speed, user_id=user_id)

        elif a_type == ActionType.ADD_DATANODE:
            count = int(params.get("count", 1))
            for _ in range(count):
                self.hdfs_service.add_datanode(session_id, user_id=user_id)

        elif a_type == ActionType.REMOVE_DATANODE:
            node_id = params.get("datanode_id") or params.get("node_id") or "datanode-1"
            self.hdfs_service.remove_datanode(session_id, node_id, user_id=user_id)

        elif a_type == ActionType.KILL_DATANODE:
            node_id = params.get("datanode_id") or params.get("node_id") or "datanode-1"
            self.hdfs_service.kill_datanode(session_id, node_id, user_id=user_id)

        elif a_type == ActionType.RECOVER_DATANODE:
            node_id = params.get("datanode_id") or params.get("node_id") or "datanode-1"
            self.hdfs_service.recover_datanode(session_id, node_id, user_id=user_id)

        recent_events = self.event_repo.get_by_session(session_id)[-1:]
        latest_evt = recent_events[0] if recent_events else None
        return True, latest_evt
