from typing import Dict, List, Tuple, Any, Optional
from app.models.simulation import SimulationStatus, SimulationStage
from app.simulation.common.enums import (
    DataNodeStatus, HeartbeatStatus, BlockState, FileStatus, HDFSEventType
)
from app.simulation.common.identifiers import DeterministicIdGenerator
from app.simulation.common.clock import SimulationClock
from app.simulation.common.exceptions import (
    HDFSFileNotFoundError, BlockNotFoundError, DataNodeNotFoundError,
    BlockDataLossError, InvalidSimulationStateError
)
from app.simulation.hdfs.cluster import HDFSClusterConfig, HDFSClusterState
from app.simulation.hdfs.namenode import NameNode
from app.simulation.hdfs.datanode import DataNode
from app.simulation.hdfs.file import HDFSFile
from app.simulation.hdfs.block import HDFSBlock, calculate_block_count
from app.simulation.hdfs.placement import BlockPlacementStrategy
from app.simulation.hdfs.replication import ReplicationManager
from app.simulation.hdfs.failure import FailureManager
from app.simulation.hdfs.recovery import RecoveryManager


class HDFSSimulationEngine:
    """Pure Python Deterministic HDFS Simulation Engine."""

    def __init__(self, config: Optional[HDFSClusterConfig] = None, initial_state: Optional[HDFSClusterState] = None):
        self.clock = SimulationClock()
        self.events: List[Dict[str, Any]] = []
        self.event_sequence: int = 1

        if initial_state:
            self.state = initial_state
            self.clock.reset(self.state.simulation_time)
        else:
            self.state = HDFSClusterState(configuration=config or HDFSClusterConfig())
            self._initialize_cluster()

    def _emit_event(self, event_type: HDFSEventType, payload: Dict[str, Any]) -> Dict[str, Any]:
        event = {
            "event_id": f"evt-hdfs-{self.event_sequence:05d}",
            "sequence_number": self.event_sequence,
            "event_type": event_type.value,
            "simulation_time": self.clock.current_time,
            "payload": payload,
        }
        self.events.append(event)
        self.event_sequence += 1
        return event

    def _initialize_cluster(self) -> None:
        cfg = self.state.configuration
        self.state.status = SimulationStatus.IDLE
        self.state.current_stage = SimulationStage.INITIALIZATION

        # Create DataNodes deterministically
        for i in range(1, cfg.data_node_count + 1):
            node_id = DeterministicIdGenerator.datanode_id(i)
            datanode = DataNode(
                node_id=node_id,
                hostname=f"{node_id}.hadoop.local",
                capacity_bytes=cfg.data_node_capacity_bytes,
                available_bytes=cfg.data_node_capacity_bytes,
                status=DataNodeStatus.LIVE,
                heartbeat_status=HeartbeatStatus.HEALTHY,
                last_heartbeat=self.clock.current_time
            )
            self.state.datanodes[node_id] = datanode

        self.clock.tick(0.5)
        self._emit_event(
            HDFSEventType.HDFS_CLUSTER_CREATED,
            {
                "cluster_id": self.state.cluster_id,
                "namenode_id": self.state.namenode.node_id,
                "datanode_count": cfg.data_node_count,
                "block_size_bytes": cfg.block_size_bytes,
                "replication_factor": cfg.replication_factor,
            }
        )

    def write_file(self, path: str, size_bytes: int) -> Tuple[HDFSFile, List[HDFSBlock]]:
        cfg = self.state.configuration
        self.clock.tick(1.0)
        self.state.status = SimulationStatus.RUNNING
        self.state.current_stage = SimulationStage.INPUT
        self.state.state_version += 1

        self._emit_event(
            HDFSEventType.FILE_WRITE_STARTED,
            {"path": path, "size_bytes": size_bytes}
        )

        file_id = DeterministicIdGenerator.file_id(len(self.state.files) + 1)
        hdfs_file = HDFSFile(
            file_id=file_id,
            path=path,
            size_bytes=size_bytes,
            block_size_bytes=cfg.block_size_bytes,
            replication_factor=cfg.replication_factor,
            status=FileStatus.WRITING
        )

        self._emit_event(
            HDFSEventType.FILE_RECEIVED,
            {"file_id": file_id, "path": path, "size_bytes": size_bytes}
        )

        # Calculate blocks and exact block size distribution
        block_count = calculate_block_count(size_bytes, cfg.block_size_bytes)
        self.state.current_stage = SimulationStage.BLOCK_CREATION

        self._emit_event(
            HDFSEventType.FILE_SPLIT,
            {"file_id": file_id, "block_count": block_count, "block_size_bytes": cfg.block_size_bytes}
        )

        created_blocks: List[HDFSBlock] = []
        remaining_bytes = size_bytes

        for idx in range(block_count):
            block_id = DeterministicIdGenerator.block_id(len(self.state.blocks) + 1)
            current_block_size = min(cfg.block_size_bytes, remaining_bytes)
            remaining_bytes -= current_block_size

            block = HDFSBlock(
                block_id=block_id,
                file_id=file_id,
                index=idx,
                size_bytes=current_block_size,
                desired_replication=cfg.replication_factor,
                state=BlockState.CREATED
            )
            created_blocks.append(block)
            hdfs_file.block_ids.append(block_id)
            self.state.blocks[block_id] = block
            self.state.namenode.metadata.register_block(block)

            self._emit_event(
                HDFSEventType.BLOCK_CREATED,
                {
                    "block_id": block_id,
                    "file_id": file_id,
                    "index": idx,
                    "size_bytes": current_block_size
                }
            )

        self.state.namenode.metadata.register_file(hdfs_file)
        self.state.files[path] = hdfs_file

        # Deterministic Replica Placement
        self.state.current_stage = SimulationStage.REPLICATION
        self._emit_event(
            HDFSEventType.BLOCK_PLACEMENT_STARTED,
            {"file_id": file_id, "block_count": len(created_blocks)}
        )

        live_nodes = [dn for dn in self.state.datanodes.values() if dn.can_serve()]

        for block in created_blocks:
            selected_nodes = BlockPlacementStrategy.select_datanodes(
                live_datanodes=live_nodes,
                block_index=block.index,
                replication_factor=cfg.replication_factor
            )

            for replica_idx, dn in enumerate(selected_nodes, start=1):
                block.replica_nodes.append(dn.node_id)
                if block.block_id not in dn.blocks:
                    dn.blocks.append(block.block_id)
                dn.used_bytes += block.size_bytes
                dn.available_bytes = max(0, dn.capacity_bytes - dn.used_bytes)

                self._emit_event(
                    HDFSEventType.BLOCK_REPLICA_CREATED,
                    {
                        "block_id": block.block_id,
                        "datanode_id": dn.node_id,
                        "replica_index": replica_idx
                    }
                )

            block.state = BlockState.HEALTHY

        self.clock.tick(1.5)
        self.state.current_stage = SimulationStage.OUTPUT
        hdfs_file.status = FileStatus.COMPLETED

        self._emit_event(
            HDFSEventType.NAMENODE_METADATA_UPDATED,
            {"path": path, "file_id": file_id, "blocks_registered": len(created_blocks)}
        )
        self._emit_event(
            HDFSEventType.FILE_WRITE_COMPLETED,
            {"path": path, "file_id": file_id, "status": "COMPLETED"}
        )

        self.state.status = SimulationStatus.COMPLETED
        self.state.current_stage = SimulationStage.INITIALIZATION
        self.state.simulation_time = self.clock.current_time
        return hdfs_file, created_blocks

    def read_file(self, path: str) -> Dict[str, Any]:
        self.clock.tick(0.5)
        self.state.state_version += 1

        self._emit_event(
            HDFSEventType.FILE_READ_STARTED,
            {"path": path}
        )

        hdfs_file = self.state.namenode.metadata.get_file(path)
        if not hdfs_file:
            self._emit_event(HDFSEventType.FILE_READ_FAILED, {"path": path, "reason": "FILE_NOT_FOUND"})
            raise HDFSFileNotFoundError(path)

        self._emit_event(
            HDFSEventType.NAMENODE_LOOKUP,
            {"path": path, "file_id": hdfs_file.file_id}
        )

        read_plan: List[Dict[str, Any]] = []

        for block_id in hdfs_file.block_ids:
            block = self.state.namenode.metadata.get_block(block_id)
            if not block:
                raise BlockNotFoundError(block_id)

            live_replicas = [
                nid for nid in block.replica_nodes
                if nid in self.state.datanodes and self.state.datanodes[nid].can_serve()
            ]

            self._emit_event(
                HDFSEventType.BLOCK_LOCATIONS_FOUND,
                {"block_id": block_id, "replica_nodes": list(block.replica_nodes), "healthy_replicas": live_replicas}
            )

            if not live_replicas or block.state == BlockState.LOST:
                self._emit_event(
                    HDFSEventType.FILE_READ_FAILED,
                    {"path": path, "failed_block_id": block_id, "reason": "DATA_LOSS"}
                )
                raise BlockDataLossError(block_id=block_id, file_path=path)

            # Choose first healthy live replica deterministically
            chosen_datanode = sorted(live_replicas)[0]

            self._emit_event(
                HDFSEventType.BLOCK_READ,
                {"block_id": block_id, "datanode_id": chosen_datanode, "size_bytes": block.size_bytes}
            )

            read_plan.append({
                "block_id": block_id,
                "selected_datanode": chosen_datanode,
                "size_bytes": block.size_bytes
            })

        self.clock.tick(0.5)
        self._emit_event(
            HDFSEventType.FILE_READ_COMPLETED,
            {"path": path, "blocks_read": len(read_plan), "total_bytes": hdfs_file.size_bytes}
        )

        self.state.simulation_time = self.clock.current_time
        return {
            "path": path,
            "file_id": hdfs_file.file_id,
            "total_bytes": hdfs_file.size_bytes,
            "read_plan": read_plan
        }

    def send_heartbeat(self, node_id: str) -> float:
        datanode = self.state.datanodes.get(node_id)
        if not datanode:
            raise DataNodeNotFoundError(node_id)

        self.clock.tick(0.1)
        datanode.last_heartbeat = self.clock.current_time
        datanode.heartbeat_status = HeartbeatStatus.HEALTHY

        self._emit_event(
            HDFSEventType.DATANODE_HEARTBEAT,
            {"node_id": node_id, "heartbeat_status": "HEALTHY", "last_heartbeat": self.clock.current_time}
        )
        self.state.simulation_time = self.clock.current_time
        return datanode.last_heartbeat

    def fail_datanode(self, node_id: str) -> Tuple[List[str], List[str]]:
        self.clock.tick(0.5)
        self.state.current_stage = SimulationStage.FAILURE
        self.state.state_version += 1

        under_replicated, lost = FailureManager.fail_datanode(
            node_id=node_id,
            datanodes=self.state.datanodes,
            namenode=self.state.namenode
        )

        self._emit_event(
            HDFSEventType.DATANODE_FAILED,
            {"node_id": node_id, "under_replicated_blocks_count": len(under_replicated), "lost_blocks_count": len(lost)}
        )

        for b_id in under_replicated:
            self._emit_event(
                HDFSEventType.BLOCK_MARKED_UNDER_REPLICATED,
                {"block_id": b_id, "remaining_replicas": len(self.state.namenode.metadata.blocks[b_id].replica_nodes)}
            )

        for b_id in lost:
            self._emit_event(
                HDFSEventType.BLOCK_MARKED_LOST,
                {"block_id": b_id}
            )

        self.state.simulation_time = self.clock.current_time
        return under_replicated, lost

    def recover_under_replicated_blocks(self) -> List[Tuple[str, str]]:
        self.clock.tick(1.0)
        self.state.current_stage = SimulationStage.RECOVERY
        self.state.state_version += 1

        self._emit_event(
            HDFSEventType.REPLICATION_STARTED,
            {"under_replicated_count": len(self.state.namenode.metadata.under_replicated_blocks)}
        )

        recovered = RecoveryManager.recover_under_replicated_blocks(
            datanodes=self.state.datanodes,
            namenode=self.state.namenode
        )

        for block_id, target_node_id in recovered:
            self._emit_event(
                HDFSEventType.REPLICA_RECOVERED,
                {"block_id": block_id, "new_datanode_id": target_node_id}
            )
            block = self.state.namenode.metadata.blocks[block_id]
            if block.state == BlockState.HEALTHY:
                self._emit_event(
                    HDFSEventType.BLOCK_REPLICATION_RESTORED,
                    {"block_id": block_id, "healthy_replicas": len(block.replica_nodes)}
                )

        self.state.current_stage = SimulationStage.INITIALIZATION
        self.state.simulation_time = self.clock.current_time
        return recovered

    def get_cluster_state(self) -> HDFSClusterState:
        self.state.simulation_time = self.clock.current_time
        return self.state

    def get_events(self) -> List[Dict[str, Any]]:
        return list(self.events)

    def clear_events(self) -> None:
        self.events.clear()

    def add_datanode(self) -> DataNode:
        cfg = self.state.configuration
        next_idx = len(self.state.datanodes) + 1
        node_id = DeterministicIdGenerator.datanode_id(next_idx)
        while node_id in self.state.datanodes:
            next_idx += 1
            node_id = DeterministicIdGenerator.datanode_id(next_idx)

        datanode = DataNode(
            node_id=node_id,
            hostname=f"{node_id}.hadoop.local",
            capacity_bytes=cfg.data_node_capacity_bytes,
            available_bytes=cfg.data_node_capacity_bytes,
            status=DataNodeStatus.LIVE,
            heartbeat_status=HeartbeatStatus.HEALTHY,
            last_heartbeat=self.clock.current_time
        )
        self.state.datanodes[node_id] = datanode
        cfg.data_node_count = len(self.state.datanodes)
        self.state.state_version += 1

        self._emit_event(
            HDFSEventType.DATANODE_ADDED,
            {
                "datanode_id": node_id,
                "hostname": datanode.hostname,
                "capacity_mb": datanode.capacity_bytes // (1024 * 1024),
                "status": "ACTIVE"
            }
        )
        return datanode

    def remove_datanode(self, node_id: str) -> List[str]:
        if node_id not in self.state.datanodes:
            raise DataNodeNotFoundError(node_id)
        if len(self.state.datanodes) <= 1:
            raise InvalidSimulationStateError("Cannot remove the last remaining DataNode from the cluster.")

        datanode = self.state.datanodes[node_id]
        under_replicated_blocks: List[str] = []

        # Remove from block replica lists
        for block in list(self.state.blocks.values()):
            if node_id in block.replica_nodes:
                block.replica_nodes.remove(node_id)
                if len(block.replica_nodes) < block.desired_replication:
                    block.state = BlockState.UNDER_REPLICATED
                    under_replicated_blocks.append(block.block_id)
                    if block.block_id not in self.state.namenode.metadata.under_replicated_blocks:
                        self.state.namenode.metadata.under_replicated_blocks.add(block.block_id)

        del self.state.datanodes[node_id]
        self.state.configuration.data_node_count = len(self.state.datanodes)
        self.state.state_version += 1

        self._emit_event(
            HDFSEventType.DATANODE_REMOVED,
            {
                "datanode_id": node_id,
                "under_replicated_blocks_count": len(under_replicated_blocks)
            }
        )
        return under_replicated_blocks

    def kill_datanode(self, node_id: str) -> Tuple[List[str], List[str]]:
        if node_id not in self.state.datanodes:
            raise DataNodeNotFoundError(node_id)
        dn = self.state.datanodes[node_id]
        if dn.status == DataNodeStatus.FAILED:
            raise InvalidSimulationStateError(f"DataNode {node_id} is already failed.")
        return self.fail_datanode(node_id)

    def recover_datanode(self, node_id: str) -> List[Tuple[str, str]]:
        if node_id not in self.state.datanodes:
            raise DataNodeNotFoundError(node_id)
        dn = self.state.datanodes[node_id]
        if dn.status == DataNodeStatus.LIVE:
            raise InvalidSimulationStateError(f"DataNode {node_id} is already live.")

        dn.status = DataNodeStatus.LIVE
        dn.heartbeat_status = HeartbeatStatus.HEALTHY
        dn.last_heartbeat = self.clock.current_time

        self._emit_event(
            HDFSEventType.REPLICA_RECOVERED,
            {"node_id": node_id, "status": "LIVE"}
        )
        return self.recover_under_replicated_blocks()

    def update_config(self, new_config: HDFSClusterConfig) -> HDFSClusterState:
        if self.state.status == SimulationStatus.RUNNING:
            raise InvalidSimulationStateError("Configuration can only be changed while simulation is idle.")

        self.state.configuration = new_config
        self.state.state_version += 1

        # Adjust DataNode count if target count differs from current count
        current_count = len(self.state.datanodes)
        target_count = new_config.data_node_count

        if target_count > current_count:
            for _ in range(target_count - current_count):
                self.add_datanode()
        elif target_count < current_count:
            nodes_to_remove = sorted(list(self.state.datanodes.keys()))[target_count:]
            for dn_id in nodes_to_remove:
                self.remove_datanode(dn_id)

        self._emit_event(
            HDFSEventType.SIMULATION_CONFIG_UPDATED,
            {
                "file_size_mb": new_config.file_size_mb,
                "block_size_mb": new_config.block_size_mb,
                "replication_factor": new_config.replication_factor,
                "datanode_count": new_config.data_node_count,
                "reducer_count": new_config.reducer_count,
                "simulation_speed": new_config.simulation_speed
            }
        )
        return self.state

    def set_speed(self, speed: float) -> float:
        if speed < 0.1 or speed > 10.0:
            raise InvalidSimulationStateError("simulation_speed must be between 0.1 and 10.0")

        self.state.configuration.simulation_speed = speed
        self.state.state_version += 1

        self._emit_event(
            HDFSEventType.SIMULATION_SPEED_CHANGED,
            {"speed": speed}
        )
        return speed

    def restart_simulation(self) -> HDFSClusterState:
        cfg = self.state.configuration
        self.clock.reset(0.0)
        self.events.clear()
        self.event_sequence = 1

        self.state = HDFSClusterState(configuration=cfg)
        self._emit_event(
            HDFSEventType.SIMULATION_RESTARTED,
            {"timestamp": 0.0, "status": "INITIALIZATION"}
        )
        self._initialize_cluster()
        return self.state

