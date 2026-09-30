from typing import List, Dict, Tuple
from app.simulation.common.enums import DataNodeStatus, BlockState
from app.simulation.hdfs.datanode import DataNode
from app.simulation.hdfs.namenode import NameNode
from app.simulation.hdfs.replication import ReplicationManager
from app.simulation.common.exceptions import DataNodeNotFoundError


class FailureManager:
    """Handles DataNode failure processing and under-replication detection."""

    @staticmethod
    def fail_datanode(
        node_id: str,
        datanodes: Dict[str, DataNode],
        namenode: NameNode
    ) -> Tuple[List[str], List[str]]:
        """
        Marks DataNode FAILED, removes it from active replica locations,
        recalculates block statuses, and returns (under_replicated_block_ids, lost_block_ids).
        """
        datanode = datanodes.get(node_id)
        if not datanode:
            raise DataNodeNotFoundError(node_id)

        datanode.status = DataNodeStatus.FAILED
        live_node_ids = {dn.node_id for dn in datanodes.values() if dn.can_serve()}

        under_replicated: List[str] = []
        lost: List[str] = []

        # Audit all blocks stored in NameNode metadata
        for block_id, block in namenode.metadata.blocks.items():
            if node_id in block.replica_nodes:
                new_state = ReplicationManager.update_block_state(block, live_node_ids)
                if new_state == BlockState.UNDER_REPLICATED:
                    under_replicated.append(block_id)
                    namenode.metadata.under_replicated_blocks.add(block_id)
                    namenode.metadata.lost_blocks.discard(block_id)
                elif new_state == BlockState.LOST:
                    lost.append(block_id)
                    namenode.metadata.lost_blocks.add(block_id)
                    namenode.metadata.under_replicated_blocks.discard(block_id)

        return under_replicated, lost
