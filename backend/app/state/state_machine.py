from datetime import datetime, timezone
from app.models.simulation import SimulationStatus, SimulationStage
from app.models.visualization import VisualizationStatus
from app.models.voice import VoiceStatus
from app.models.event import EventType
from app.state.session_state import SessionState
from app.core.exceptions import InvalidStateTransitionError


class StateMachine:
    """Deterministic State Machine managing SessionState transitions."""

    @staticmethod
    def start_simulation(state: SessionState) -> EventType:
        current_status = state.simulation.status
        if current_status in [SimulationStatus.RUNNING]:
            raise InvalidStateTransitionError(
                current_status=current_status,
                action="START",
                allowed_states=[SimulationStatus.IDLE, SimulationStatus.PAUSED, SimulationStatus.COMPLETED, SimulationStatus.FAILED]
            )

        now = datetime.now(timezone.utc)
        state.simulation.status = SimulationStatus.RUNNING
        state.simulation.started_at = state.simulation.started_at or now
        state.simulation.updated_at = now
        state.visualization.status = VisualizationStatus.PLAYING
        state.session.updated_at = now
        state.session.last_activity_at = now
        state.state_version += 1

        return EventType.SIMULATION_STARTED

    @staticmethod
    def pause_simulation(state: SessionState) -> EventType:
        current_status = state.simulation.status
        if current_status != SimulationStatus.RUNNING:
            raise InvalidStateTransitionError(
                current_status=current_status,
                action="PAUSE",
                allowed_states=[SimulationStatus.RUNNING]
            )

        now = datetime.now(timezone.utc)
        state.simulation.status = SimulationStatus.PAUSED
        state.simulation.updated_at = now
        state.visualization.status = VisualizationStatus.PAUSED
        state.voice.status = VoiceStatus.INTERRUPTED
        state.voice.is_speaking = False
        state.voice.interruption_requested = True
        state.session.updated_at = now
        state.session.last_activity_at = now
        state.state_version += 1

        return EventType.SIMULATION_PAUSED

    @staticmethod
    def resume_simulation(state: SessionState) -> EventType:
        current_status = state.simulation.status
        if current_status != SimulationStatus.PAUSED:
            raise InvalidStateTransitionError(
                current_status=current_status,
                action="RESUME",
                allowed_states=[SimulationStatus.PAUSED]
            )

        now = datetime.now(timezone.utc)
        state.simulation.status = SimulationStatus.RUNNING
        state.simulation.updated_at = now
        state.visualization.status = VisualizationStatus.PLAYING
        state.voice.status = VoiceStatus.IDLE
        state.voice.interruption_requested = False
        state.session.updated_at = now
        state.session.last_activity_at = now
        state.state_version += 1

        return EventType.SIMULATION_RESUMED

    @staticmethod
    def restart_simulation(state: SessionState) -> EventType:
        now = datetime.now(timezone.utc)
        state.simulation.status = SimulationStatus.RUNNING
        state.simulation.current_stage = SimulationStage.INITIALIZATION
        state.simulation.progress = 0.0
        state.simulation.simulation_time = 0.0
        state.simulation.started_at = now
        state.simulation.updated_at = now
        state.visualization.status = VisualizationStatus.PLAYING
        state.visualization.animation_progress = 0.0
        state.voice.status = VoiceStatus.IDLE
        state.voice.is_speaking = False
        state.voice.interruption_requested = False
        state.session.updated_at = now
        state.session.last_activity_at = now
        state.state_version += 1

        return EventType.SIMULATION_RESTARTED
