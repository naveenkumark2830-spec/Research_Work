from typing import Dict, List, Tuple
from app.simulation.common.enums import BlockState
from app.simulation.hdfs.datanode import DataNode
from app.simulation.hdfs.namenode import NameNode
from app.simulation.hdfs.placement import BlockPlacementStrategy
from app.simulation.common.exceptions import InsufficientDataNodesError


class RecoveryManager:
    """Handles re-replication of under-replicated blocks to healthy DataNodes."""

    @staticmethod
    def recover_under_replicated_blocks(
        datanodes: Dict[str, DataNode],
        namenode: NameNode
    ) -> List[Tuple[str, str]]:
        """
        Scans under_replicated_blocks set, deterministically selects replacement nodes,
        places replacement replicas, updates metadata, and restores block state to HEALTHY.
        Returns list of (block_id, new_datanode_id).
        """
        recovered_replicas: List[Tuple[str, str]] = []
        under_replicated_list = sorted(list(namenode.metadata.under_replicated_blocks))
        live_nodes = [dn for dn in datanodes.values() if dn.can_serve()]
        live_node_ids = {dn.node_id for dn in live_nodes}

        for block_id in under_replicated_list:
            block = namenode.metadata.blocks.get(block_id)
            if not block or block.state == BlockState.LOST:
                continue

            current_replicas = set(block.replica_nodes)
            needed_replicas = block.desired_replication - len(current_replicas)

            if needed_replicas <= 0:
                block.state = BlockState.HEALTHY
                namenode.metadata.under_replicated_blocks.discard(block_id)
                continue

            # Select replacement DataNodes deterministically
            available_replacement_nodes = [
                dn for dn in live_nodes if dn.node_id not in current_replicas
            ]
            available_replacement_nodes.sort(key=lambda dn: dn.node_id)

            if not available_replacement_nodes:
                # Cannot recover yet because no available extra healthy DataNodes exist
                continue

            nodes_to_add = available_replacement_nodes[:needed_replicas]
            for target_node in nodes_to_add:
                block.replica_nodes.append(target_node.node_id)
                if block.block_id not in target_node.blocks:
                    target_node.blocks.append(block.block_id)
                target_node.used_bytes += block.size_bytes
                target_node.available_bytes = max(0, target_node.capacity_bytes - target_node.used_bytes)
                recovered_replicas.append((block_id, target_node.node_id))

            # Recalculate block state
            if len(set(block.replica_nodes)) >= block.desired_replication:
                block.state = BlockState.HEALTHY
                namenode.metadata.under_replicated_blocks.discard(block_id)

        return recovered_replicas
