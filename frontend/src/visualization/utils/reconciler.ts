import {
  VisualClusterState,
  VisualNode,
  VisualBlock,
  VisualNodeHealth,
  VisualBlockState,
  InspectorTarget
} from '../types/visualization';

export function calculateNodeLayout(
  nodeCount: number,
  index: number,
  canvasWidth: number = 1000,
  startY: number = 380
): { x: number; y: number } {
  if (nodeCount <= 1) {
    return { x: canvasWidth / 2, y: startY };
  }
  const marginX = 120;
  const availableWidth = canvasWidth - 2 * marginX;
  const step = availableWidth / (nodeCount - 1);
  return {
    x: marginX + index * step,
    y: startY
  };
}

export function reconcileClusterState(
  clusterState: Record<string, any> | null,
  previousSelectedTarget: InspectorTarget | null = null
): VisualClusterState {
  if (!clusterState) {
    return {
      cluster_id: 'cls_default',
      nodes: {
        'client-0': {
          id: 'client-0',
          type: 'CLIENT',
          label: 'DFS Client',
          hostname: 'client.hadoop.local',
          status: 'READY',
          health: 'HEALTHY',
          x: 120,
          y: 100,
          capacity_bytes: 0,
          used_bytes: 0,
          blocks: []
        },
        'nn-0': {
          id: 'nn-0',
          type: 'NAMENODE',
          label: 'NameNode',
          hostname: 'namenode.hadoop.local',
          status: 'ACTIVE',
          health: 'HEALTHY',
          x: 500,
          y: 100,
          capacity_bytes: 0,
          used_bytes: 0,
          blocks: []
        }
      },
      blocks: {},
      transfers: [],
      selected_target: previousSelectedTarget,
      simulation_time: 0.0,
      state_version: 1,
      file_count: 0,
      total_capacity: 0,
      used_capacity: 0
    };
  }

  const nodes: Record<string, VisualNode> = {};

  // Client Node
  nodes['client-0'] = {
    id: 'client-0',
    type: 'CLIENT',
    label: 'DFS Client',
    hostname: 'client.hadoop.local',
    status: 'READY',
    health: 'HEALTHY',
    x: 120,
    y: 100,
    capacity_bytes: 0,
    used_bytes: 0,
    blocks: []
  };

  // NameNode Node
  const rawNamenode = clusterState.namenode || {};
  const nnId = rawNamenode.node_id || 'nn-0';
  nodes[nnId] = {
    id: nnId,
    type: 'NAMENODE',
    label: 'NameNode',
    hostname: 'namenode.hadoop.local',
    status: rawNamenode.status || 'ACTIVE',
    health: rawNamenode.status === 'ACTIVE' ? 'HEALTHY' : 'FAILED',
    x: 500,
    y: 100,
    capacity_bytes: 0,
    used_bytes: 0,
    blocks: []
  };

  // DataNodes
  const rawDatanodes = clusterState.datanodes || {};
  const dnKeys = Object.keys(rawDatanodes).sort();
  let totalCap = 0;
  let totalUsed = 0;

  dnKeys.forEach((key, index) => {
    const dn = rawDatanodes[key];
    const pos = calculateNodeLayout(dnKeys.length, index);
    const capacity = dn.capacity_bytes || 107374182400;
    const used = dn.used_bytes || 0;
    totalCap += capacity;
    totalUsed += used;

    let health: VisualNodeHealth = 'HEALTHY';
    const dnStatus = (dn.status || 'LIVE').toUpperCase();
    const hbStatus = (dn.heartbeat_status || 'HEALTHY').toUpperCase();

    if (dnStatus === 'DEAD' || dnStatus === 'FAILED' || hbStatus === 'DEAD') {
      health = 'FAILED';
    } else if (hbStatus === 'DEGRADED') {
      health = 'DEGRADED';
    }

    nodes[dn.node_id] = {
      id: dn.node_id,
      type: 'DATANODE',
      label: `DataNode ${index + 1}`,
      hostname: dn.hostname || `dn${index + 1}.hadoop.local`,
      status: dnStatus,
      health,
      x: pos.x,
      y: pos.y,
      capacity_bytes: capacity,
      used_bytes: used,
      blocks: dn.blocks || [],
      last_heartbeat: dn.last_heartbeat || 0,
      rack_id: dn.rack_id || '/default-rack'
    };
  });

  // Blocks
  const rawBlocks = clusterState.blocks || {};
  const blocks: Record<string, VisualBlock> = {};

  Object.keys(rawBlocks).forEach((bKey) => {
    const b = rawBlocks[bKey];
    let bState: VisualBlockState = (b.state || 'WRITTEN').toUpperCase() as VisualBlockState;
    
    // Determine state if under-replicated or over-replicated
    const replicaCount = (b.replica_nodes || []).length;
    const desired = b.desired_replication || 3;

    if (bState === 'WRITTEN' || bState === 'ALLOCATED') {
      if (replicaCount === 0) {
        bState = 'CORRUPT';
      } else if (replicaCount < desired) {
        bState = 'UNDER_REPLICATED';
      } else if (replicaCount > desired) {
        bState = 'OVER_REPLICATED';
      }
    }

    blocks[b.block_id] = {
      block_id: b.block_id,
      file_id: b.file_id || '',
      index: b.index !== undefined ? b.index : 0,
      size_bytes: b.size_bytes || 0,
      replica_nodes: b.replica_nodes || [],
      desired_replication: desired,
      state: bState
    };
  });

  const filesCount = Object.keys(clusterState.files || {}).length;

  return {
    cluster_id: clusterState.cluster_id || 'cls_1',
    nodes,
    blocks,
    transfers: [],
    selected_target: previousSelectedTarget,
    simulation_time: clusterState.simulation_time || 0.0,
    state_version: clusterState.state_version || 1,
    file_count: filesCount,
    total_capacity: totalCap,
    used_capacity: totalUsed
  };
}
