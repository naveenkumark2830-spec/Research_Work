import copy
from app.state.session_state import SessionState
from app.models.event import Event
from app.models.simulation import SimulationStatus, SimulationStage
from app.models.conversation import Message, MessageRole
from app.simulation.hdfs.cluster import HDFSClusterConfig, HDFSClusterState
from app.simulation.hdfs.datanode import DataNode
from app.simulation.common.enums import DataNodeStatus, HeartbeatStatus, BlockState, FileStatus
from app.simulation.hdfs.file import HDFSFile
from app.simulation.hdfs.block import HDFSBlock


class EventApplier:
    """Pure state transformation applier applying events onto SessionState."""

    @staticmethod
    def apply_event(state: SessionState, event: Event) -> SessionState:
        # Create shallow/deep working copy to preserve state immutability during replay
        state_copy = state.model_copy(deep=True)
        evt_type = event.event_type
        payload = event.payload or {}

        # Track state version and simulation time
        state_copy.state_version = event.state_version
        state_copy.simulation.simulation_time = event.logical_timestamp

        # Standard State Engine Events
        if evt_type == "SESSION_CREATED":
            if "topic" in payload:
                state_copy.session.current_topic = payload["topic"]

        elif evt_type == "CONVERSATION_MESSAGE_ADDED":
            if "message_id" in payload:
                role = MessageRole(payload.get("role", "USER"))
                msg = Message(
                    message_id=payload["message_id"],
                    role=role,
                    content=payload.get("content", ""),
                    timestamp=event.timestamp
                )
                state_copy.conversation.recent_messages.append(msg)
                state_copy.conversation.conversation_turn_count += 1
                if role == MessageRole.USER:
                    state_copy.conversation.last_user_message = msg.content
                elif role == MessageRole.ASSISTANT:
                    state_copy.conversation.last_assistant_message = msg.content

        elif evt_type == "SIMULATION_STARTED":
            state_copy.simulation.status = SimulationStatus.RUNNING
            state_copy.visualization.status = "PLAYING"

        elif evt_type == "SIMULATION_PAUSED":
            state_copy.simulation.status = SimulationStatus.PAUSED
            state_copy.visualization.status = "PAUSED"
            state_copy.voice.status = "INTERRUPTED"

        elif evt_type == "SIMULATION_RESUMED":
            state_copy.simulation.status = SimulationStatus.RUNNING
            state_copy.visualization.status = "PLAYING"
            state_copy.voice.status = "IDLE"

        elif evt_type == "SIMULATION_RESTARTED":
            state_copy.simulation.status = SimulationStatus.RUNNING
            state_copy.simulation.current_stage = SimulationStage.INITIALIZATION
            state_copy.simulation.progress = 0.0

        # HDFS Simulation Events
        elif evt_type == "HDFS_CLUSTER_CREATED" or payload.get("sim_event_type") == "HDFS_CLUSTER_CREATED":
            state_copy.simulation.status = SimulationStatus.RUNNING
            dn_count = payload.get("datanode_count", 5)
            block_size = payload.get("block_size_bytes", 134217728)
            repl_factor = payload.get("replication_factor", 3)

            cluster_cfg = HDFSClusterConfig(
                data_node_count=dn_count,
                block_size_bytes=block_size,
                replication_factor=repl_factor
            )
            cluster_state = HDFSClusterState(configuration=cluster_cfg)
            for i in range(1, dn_count + 1):
                node_id = f"datanode-{i}"
                cluster_state.datanodes[node_id] = DataNode(
                    node_id=node_id,
                    hostname=f"{node_id}.hadoop.local",
                    capacity_bytes=cluster_cfg.data_node_capacity_bytes,
                    available_bytes=cluster_cfg.data_node_capacity_bytes,
                    status=DataNodeStatus.LIVE
                )
            state_copy.simulation.configuration.custom_parameters["hdfs_cluster_state"] = cluster_state.model_dump(mode="json")

        # Handle HDFS sub-events embedded in SIMULATION_UPDATED payload or direct event types
        sim_evt_type = payload.get("sim_event_type", evt_type)

        raw_cluster = state_copy.simulation.configuration.custom_parameters.get("hdfs_cluster_state")
        if raw_cluster:
            cluster_state = HDFSClusterState.model_validate(raw_cluster)

            if sim_evt_type == "FILE_WRITE_STARTED":
                state_copy.simulation.status = SimulationStatus.RUNNING
                cluster_state.current_stage = SimulationStage.INPUT
            elif sim_evt_type == "FILE_SPLIT":
                cluster_state.current_stage = SimulationStage.BLOCK_CREATION
            elif sim_evt_type == "BLOCK_CREATED":
                b_id = payload["block_id"]
                f_id = payload["file_id"]
                size = payload["size_bytes"]
                b_idx = payload["index"]
                block = HDFSBlock(
                    block_id=b_id,
                    file_id=f_id,
                    index=b_idx,
                    size_bytes=size,
                    state=BlockState.CREATED
                )
                cluster_state.blocks[b_id] = block
                cluster_state.namenode.metadata.register_block(block)
            elif sim_evt_type == "BLOCK_REPLICA_CREATED":
                b_id = payload["block_id"]
                dn_id = payload["datanode_id"]
                if b_id in cluster_state.blocks:
                    block = cluster_state.blocks[b_id]
                    if dn_id not in block.replica_nodes:
                        block.replica_nodes.append(dn_id)
                    block.state = BlockState.HEALTHY
                if dn_id in cluster_state.datanodes:
                    dn = cluster_state.datanodes[dn_id]
                    if b_id not in dn.blocks:
                        dn.blocks.append(b_id)
            elif sim_evt_type == "FILE_WRITE_COMPLETED":
                state_copy.simulation.status = SimulationStatus.COMPLETED
                cluster_state.current_stage = SimulationStage.INITIALIZATION
                path = payload.get("path", "file.csv")
                f_id = payload.get("file_id", "file-00001")
                hdfs_file = HDFSFile(
                    file_id=f_id,
                    path=path,
                    size_bytes=payload.get("size_bytes", 524288000),
                    block_size_bytes=cluster_state.configuration.block_size_bytes,
                    block_ids=list(cluster_state.blocks.keys()),
                    status=FileStatus.COMPLETED
                )
                cluster_state.files[path] = hdfs_file
                cluster_state.namenode.metadata.register_file(hdfs_file)
            elif sim_evt_type == "DATANODE_FAILED":
                dn_id = payload["node_id"]
                if dn_id in cluster_state.datanodes:
                    cluster_state.datanodes[dn_id].status = DataNodeStatus.FAILED
                cluster_state.current_stage = SimulationStage.FAILURE
            elif sim_evt_type == "BLOCK_MARKED_UNDER_REPLICATED":
                b_id = payload["block_id"]
                if b_id in cluster_state.blocks:
                    cluster_state.blocks[b_id].state = BlockState.UNDER_REPLICATED
                    cluster_state.namenode.metadata.under_replicated_blocks.add(b_id)
            elif sim_evt_type == "BLOCK_MARKED_LOST":
                b_id = payload["block_id"]
                if b_id in cluster_state.blocks:
                    cluster_state.blocks[b_id].state = BlockState.LOST
                    cluster_state.namenode.metadata.lost_blocks.add(b_id)
            elif sim_evt_type == "REPLICA_RECOVERED":
                b_id = payload["block_id"]
                dn_id = payload["new_datanode_id"]
                if b_id in cluster_state.blocks:
                    block = cluster_state.blocks[b_id]
                    if dn_id not in block.replica_nodes:
                        block.replica_nodes.append(dn_id)
                if dn_id in cluster_state.datanodes:
                    dn = cluster_state.datanodes[dn_id]
                    if b_id not in dn.blocks:
                        dn.blocks.append(b_id)
            elif sim_evt_type == "BLOCK_REPLICATION_RESTORED":
                b_id = payload["block_id"]
                if b_id in cluster_state.blocks:
                    cluster_state.blocks[b_id].state = BlockState.HEALTHY
                    cluster_state.namenode.metadata.under_replicated_blocks.discard(b_id)

            cluster_state.simulation_time = event.logical_timestamp
            state_copy.simulation.configuration.custom_parameters["hdfs_cluster_state"] = cluster_state.model_dump(mode="json")

        return state_copy
