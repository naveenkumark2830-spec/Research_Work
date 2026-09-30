import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.state.session_state import SessionState
from app.models.simulation import SimulationSystem, SimulationStatus, SimulationStage
from app.models.event import Event, EventCategory, EventType
from app.core.exceptions import ResourceNotFoundError, UserIsolationError
from app.repositories.session_repository import ISessionRepository
from app.repositories.event_repository import IEventRepository
from app.simulation.common.exceptions import InvalidSimulationStateError
from app.simulation.hdfs.cluster import HDFSClusterConfig, HDFSClusterState
from app.simulation.hdfs.engine import HDFSSimulationEngine


class HDFSService:
    def __init__(
        self,
        session_repo: ISessionRepository,
        event_repo: IEventRepository
    ):
        self.session_repo = session_repo
        self.event_repo = event_repo

    def _get_or_create_engine(self, state: SessionState, config: Optional[HDFSClusterConfig] = None) -> HDFSSimulationEngine:
        state.simulation.system = SimulationSystem.HDFS

        raw_cluster_state = state.simulation.configuration.custom_parameters.get("hdfs_cluster_state")
        if raw_cluster_state:
            cluster_state = HDFSClusterState.model_validate(raw_cluster_state)
            engine = HDFSSimulationEngine(initial_state=cluster_state)
        else:
            cluster_cfg = config or HDFSClusterConfig(
                file_size_mb=state.simulation.configuration.file_size_mb or 500,
                block_size_mb=state.simulation.configuration.block_size_mb or 128,
                replication_factor=state.simulation.configuration.replication_factor or 3,
                data_node_count=state.simulation.configuration.datanode_count or 5,
                reducer_count=state.simulation.configuration.reducer_count or 5,
                simulation_speed=state.simulation.configuration.simulation_speed or 1.0,
            )
            engine = HDFSSimulationEngine(config=cluster_cfg)

        return engine

    def _save_engine_state(self, state: SessionState, engine: HDFSSimulationEngine) -> SessionState:
        cluster_state = engine.get_cluster_state()

        state.simulation.status = cluster_state.status
        state.simulation.current_stage = cluster_state.current_stage
        state.simulation.simulation_time = cluster_state.simulation_time

        # Mirror configuration fields into SessionState.configuration
        cfg = cluster_state.configuration
        state.simulation.configuration.file_size_mb = cfg.file_size_mb
        state.simulation.configuration.block_size_mb = cfg.block_size_mb
        state.simulation.configuration.replication_factor = cfg.replication_factor
        state.simulation.configuration.datanode_count = cfg.data_node_count
        state.simulation.configuration.reducer_count = cfg.reducer_count
        state.simulation.configuration.simulation_speed = cfg.simulation_speed
        state.simulation.configuration.file_size = cfg.file_size_bytes
        state.simulation.configuration.block_size = cfg.block_size_bytes
        state.simulation.configuration.data_node_count = cfg.data_node_count

        state.simulation.configuration.custom_parameters["hdfs_cluster_state"] = cluster_state.model_dump(mode="json")
        state.state_version += 1
        state.session.updated_at = datetime.now(timezone.utc)

        now = datetime.now(timezone.utc)
        for sim_evt in engine.get_events():
            seq_num = self.event_repo.get_next_sequence_number(state.session.session_id)
            event = Event(
                event_id=f"evt_{uuid.uuid4().hex[:12]}",
                session_id=state.session.session_id,
                category=EventCategory.HDFS,
                event_type=sim_evt["event_type"],
                timestamp=now,
                sequence_number=seq_num,
                payload={
                    "sim_event_type": sim_evt["event_type"],
                    "sim_event_id": sim_evt["event_id"],
                    "sim_time": sim_evt["simulation_time"],
                    **sim_evt["payload"]
                },
                state_version=state.state_version
            )
            self.event_repo.save(event)

        engine.clear_events()
        self.session_repo.save_state(state)
        return state

    def create_cluster(
        self,
        session_id: str,
        config: Optional[HDFSClusterConfig] = None,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state, config)
        return self._save_engine_state(state, engine)

    def update_config(
        self,
        session_id: str,
        config: HDFSClusterConfig,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        if state.simulation.status == SimulationStatus.RUNNING:
            raise InvalidSimulationStateError("Configuration can only be changed while simulation is idle.")

        engine = self._get_or_create_engine(state, config)
        engine.update_config(config)
        return self._save_engine_state(state, engine)

    def write_file(
        self,
        session_id: str,
        path: str,
        size_bytes: int,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        engine.write_file(path, size_bytes)
        state.simulation.progress = 1.0
        return self._save_engine_state(state, engine)

    def read_file(
        self,
        session_id: str,
        path: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        result = engine.read_file(path)
        self._save_engine_state(state, engine)
        return result

    def add_datanode(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        engine.add_datanode()
        return self._save_engine_state(state, engine)

    def remove_datanode(
        self,
        session_id: str,
        node_id: str,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        engine.remove_datanode(node_id)
        return self._save_engine_state(state, engine)

    def kill_datanode(
        self,
        session_id: str,
        node_id: str,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        engine.kill_datanode(node_id)
        return self._save_engine_state(state, engine)

    def recover_datanode(
        self,
        session_id: str,
        node_id: str,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        engine.recover_datanode(node_id)
        return self._save_engine_state(state, engine)

    def recover_under_replicated_blocks(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        engine.recover_under_replicated_blocks()
        return self._save_engine_state(state, engine)

    def set_speed(
        self,
        session_id: str,
        speed: float,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        engine.set_speed(speed)
        return self._save_engine_state(state, engine)

    def restart_simulation(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> SessionState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        engine.restart_simulation()
        return self._save_engine_state(state, engine)

    def get_hdfs_cluster_state(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> HDFSClusterState:
        state = self.session_repo.get_state(session_id)
        if not state:
            raise ResourceNotFoundError("Session", session_id)
        if user_id and state.user.user_id != user_id:
            raise UserIsolationError(user_id, session_id)

        engine = self._get_or_create_engine(state)
        return engine.get_cluster_state()
