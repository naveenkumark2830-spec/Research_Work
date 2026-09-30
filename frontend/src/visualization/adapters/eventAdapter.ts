import { Event } from '../../types/session';
import { VisualClusterState, VisualTransfer } from '../types/visualization';

export function deriveTransfersFromEvent(
  event: Event,
  visualState: VisualClusterState
): VisualTransfer[] {
  const payload = event.payload || {};
  const eventType = event.event_type;
  const transfers: VisualTransfer[] = [];

  // Heartbeat event: DataNode -> NameNode ping
  if (eventType === 'HEARTBEAT_RECEIVED' || eventType === 'DATANODE_HEARTBEAT') {
    const dnId = payload.datanode_id || payload.node_id;
    const nnId = Object.keys(visualState.nodes).find(
      (k) => visualState.nodes[k].type === 'NAMENODE'
    ) || 'nn-0';

    if (dnId && visualState.nodes[dnId]) {
      transfers.push({
        id: `tr_${event.event_id || event.sequence_number}_hb`,
        source_node_id: dnId,
        target_node_id: nnId,
        type: 'HEARTBEAT',
        progress: 0.5,
        label: 'Heartbeat Ping'
      });
    }
  }

  // Block Allocation / File Write: Client -> NameNode request, Client -> Primary DataNode write
  if (eventType === 'BLOCK_ALLOCATED' || eventType === 'FILE_WRITE_STARTED') {
    const targetNodes = payload.target_nodes || payload.replica_nodes || [];
    const primaryDn = targetNodes[0];

    if (primaryDn && visualState.nodes[primaryDn]) {
      transfers.push({
        id: `tr_${event.sequence_number}_client_write`,
        source_node_id: 'client-0',
        target_node_id: primaryDn,
        block_id: payload.block_id,
        type: 'CLIENT_WRITE',
        progress: 0.8,
        label: `Writing ${payload.block_id || 'Block'}`
      });
    }
  }

  // Pipeline replica write / Replication Task: DataNode -> DataNode
  if (eventType === 'BLOCK_REPLICA_WRITTEN' || eventType === 'REPLICATION_TASK_SCHEDULED') {
    const srcNode = payload.source_node_id || payload.node_id;
    const targetNode = payload.target_node_id || payload.target_datanode_id;
    
    if (srcNode && targetNode && visualState.nodes[srcNode] && visualState.nodes[targetNode]) {
      transfers.push({
        id: `tr_${event.sequence_number}_repl`,
        source_node_id: srcNode,
        target_node_id: targetNode,
        block_id: payload.block_id,
        type: 'REPLICATION',
        progress: 0.6,
        label: `Replicating ${payload.block_id || 'Block'}`
      });
    }
  }

  return transfers;
}

export function processEventForVisualization(
  event: Event,
  currentState: VisualClusterState
): VisualClusterState {
  const newTransfers = deriveTransfersFromEvent(event, currentState);

  // Keep last 3 active transfers for animation effects
  const combinedTransfers = [...newTransfers, ...currentState.transfers].slice(0, 4);

  return {
    ...currentState,
    transfers: combinedTransfers,
    state_version: event.state_version || currentState.state_version
  };
}
