from typing import Dict
from app.simulation.common.enums import BlockState
from app.simulation.hdfs.block import HDFSBlock


class ReplicationManager:
    """Manages and evaluates HDFS block replication status."""

    @staticmethod
    def get_replication_status(block: HDFSBlock, live_datanode_ids: set[str]) -> BlockState:
        """
        Determines current BlockState based on active healthy replicas.
        Filters replica_nodes against live_datanode_ids.
        """
        active_replicas = set(block.replica_nodes).intersection(live_datanode_ids)
        active_count = len(active_replicas)

        if active_count == 0:
            return BlockState.LOST
        elif active_count < block.desired_replication:
            return BlockState.UNDER_REPLICATED
        else:
            return BlockState.HEALTHY

    @staticmethod
    def update_block_state(block: HDFSBlock, live_datanode_ids: set[str]) -> BlockState:
        """Updates block state and returns the new status."""
        # Prune non-live nodes from active block replicas
        block.replica_nodes = [node_id for node_id in block.replica_nodes if node_id in live_datanode_ids]
        new_state = ReplicationManager.get_replication_status(block, live_datanode_ids)
        block.state = new_state
        return new_state
