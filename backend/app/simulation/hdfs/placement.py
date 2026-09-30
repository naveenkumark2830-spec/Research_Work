from typing import List
from app.simulation.hdfs.datanode import DataNode
from app.simulation.common.exceptions import InsufficientDataNodesError


class BlockPlacementStrategy:
    """Deterministic Round-Robin Block Replica Placement Strategy."""

    @staticmethod
    def select_datanodes(
        live_datanodes: List[DataNode],
        block_index: int,
        replication_factor: int,
        exclude_node_ids: List[str] = None
    ) -> List[DataNode]:
        """
        Deterministically selects `replication_factor` unique live DataNodes
        for a block using round-robin indexing.
        """
        exclude_set = set(exclude_node_ids or [])
        available_nodes = [dn for dn in live_datanodes if dn.can_serve() and dn.node_id not in exclude_set]

        # Sort nodes by ID to guarantee deterministic ordering regardless of dictionary order
        available_nodes.sort(key=lambda dn: dn.node_id)

        if len(available_nodes) < replication_factor:
            raise InsufficientDataNodesError(required=replication_factor, available=len(available_nodes))

        total_nodes = len(available_nodes)
        start_offset = (block_index * replication_factor) % total_nodes

        selected: List[DataNode] = []
        for i in range(replication_factor):
            idx = (start_offset + i) % total_nodes
            selected.append(available_nodes[idx])

        return selected
