import React from 'react';
import { VisualTransfer, VisualNode } from '../types/visualization';

interface TransferAnimationProps {
  transfer: VisualTransfer;
  nodes: Record<string, VisualNode>;
}

export const TransferAnimation: React.FC<TransferAnimationProps> = ({
  transfer,
  nodes
}) => {
  const sourceId = transfer.source_node_id || (transfer as any).source_id;
  const targetId = transfer.target_node_id || (transfer as any).target_id;
  const sourceNode = nodes[sourceId];
  const targetNode = nodes[targetId];

  if (!sourceNode || !targetNode) {
    return null;
  }

  const x1 = sourceNode.x;
  const y1 = sourceNode.y;
  const x2 = targetNode.x;
  const y2 = targetNode.y;

  // Control point for smooth curve
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2 - (transfer.type === 'HEARTBEAT' ? 30 : -20);
  const pathD = `M ${x1} ${y1} Q ${midX} ${midY} ${x2} ${y2}`;

  const isHeartbeat = transfer.type === 'HEARTBEAT';
  const isClientWrite = transfer.type === 'CLIENT_WRITE';

  const strokeHex = isHeartbeat
    ? 'rgba(34, 197, 94, 0.8)'
    : isClientWrite
    ? 'rgba(0, 240, 255, 0.9)'
    : 'rgba(245, 158, 11, 0.9)';

  const fillHex = isHeartbeat
    ? '#22c55e'
    : isClientWrite
    ? '#00f0ff'
    : '#f59e0b';

  return (
    <g style={{ pointerEvents: 'none' }}>
      {/* Background dashed path */}
      <path
        d={pathD}
        fill="none"
        stroke={strokeHex}
        strokeWidth="2"
        strokeDasharray="4 4"
      />

      {/* Moving animated packet along SVG path */}
      <circle r={isHeartbeat ? 4 : 6} fill={fillHex}>
        <animateMotion
          path={pathD}
          dur={isHeartbeat ? '1.2s' : '2.0s'}
          repeatCount="indefinite"
        />
      </circle>

      {/* Label on path */}
      {transfer.label && (
        <text
          x={midX}
          y={midY - 8}
          textAnchor="middle"
          fill="#f8fafc"
          fontSize="9"
          fontFamily="'JetBrains Mono', monospace"
        >
          {transfer.label}
        </text>
      )}
    </g>
  );
};
