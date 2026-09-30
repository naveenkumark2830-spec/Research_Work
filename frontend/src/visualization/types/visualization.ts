export type VisualNodeType = 'CLIENT' | 'NAMENODE' | 'DATANODE';
export type VisualNodeHealth = 'HEALTHY' | 'DEGRADED' | 'FAILED';
export type VisualBlockState = 'CREATED' | 'ALLOCATED' | 'WRITTEN' | 'UNDER_REPLICATED' | 'OVER_REPLICATED' | 'CORRUPT';
export type TransferType = 'CLIENT_WRITE' | 'REPLICATION' | 'HEARTBEAT';
export type InspectorTargetType = 'NAMENODE' | 'DATANODE' | 'FILE' | 'BLOCK';

export interface VisualNode {
  id: string;
  type: VisualNodeType;
  label: string;
  hostname: string;
  status: string;
  health: VisualNodeHealth;
  x: number;
  y: number;
  capacity_bytes: number;
  used_bytes: number;
  blocks: string[];
  last_heartbeat?: number;
  rack_id?: string;
}

export interface VisualBlock {
  block_id: string;
  file_id: string;
  index: number;
  size_bytes: number;
  replica_nodes: string[];
  desired_replication: number;
  state: VisualBlockState;
}

export interface VisualTransfer {
  id: string;
  source_node_id: string;
  target_node_id: string;
  block_id?: string;
  type: TransferType;
  progress: number;
  label?: string;
}

export interface InspectorTarget {
  type: InspectorTargetType;
  id: string;
  data: Record<string, any>;
}

export interface VisualClusterState {
  cluster_id: string;
  nodes: Record<string, VisualNode>;
  blocks: Record<string, VisualBlock>;
  transfers: VisualTransfer[];
  selected_target: InspectorTarget | null;
  simulation_time: number;
  state_version: number;
  file_count: number;
  total_capacity: number;
  used_capacity: number;
}
