import React from 'react';
import { VisualBlock, VisualBlockState } from '../types/visualization';

interface HDFSBlockNodeProps {
  block: VisualBlock;
  onClick?: (block: VisualBlock) => void;
  isSelected?: boolean;
}

export const getBlockColor = (state: VisualBlockState): string => {
  switch (state) {
    case 'CREATED':
    case 'ALLOCATED':
      return '#3b82f6'; // Blue
    case 'WRITTEN':
      return '#10b981'; // Green (Healthy)
    case 'UNDER_REPLICATED':
      return '#f59e0b'; // Amber / Yellow
    case 'OVER_REPLICATED':
      return '#8b5cf6'; // Purple
    case 'CORRUPT':
      return '#ef4444'; // Red
    default:
      return '#6b7280'; // Gray
  }
};

export const HDFSBlockNode: React.FC<HDFSBlockNodeProps> = ({
  block,
  onClick,
  isSelected = false
}) => {
  const state = block.state || (block as any).status || 'WRITTEN';
  const color = getBlockColor(state);
  const replicaCount = (block.replica_nodes || (block as any).replicas || []).length;
  const desiredRep = block.desired_replication || 3;
  const blockId = block.block_id || 'block-unk';

  return (
    <button
      onClick={() => onClick && onClick(block)}
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-mono transition-all border ${
        isSelected
          ? 'ring-2 ring-indigo-500 border-indigo-500 font-bold shadow-md'
          : 'border-slate-700 hover:border-slate-500'
      }`}
      style={{ backgroundColor: `${color}15`, color: color }}
      title={`Block: ${blockId}\nState: ${state}\nReplicas: ${replicaCount}/${desiredRep}`}
    >
      <span
        className="w-2 h-2 rounded-full inline-block animate-pulse"
        style={{ backgroundColor: color }}
      />
      <span>{blockId.slice(0, 10)}</span>
      <span className="text-[10px] opacity-75">
        [{replicaCount}/{desiredRep}]
      </span>
    </button>
  );
};
