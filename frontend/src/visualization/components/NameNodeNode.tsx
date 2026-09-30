import React from 'react';
import { VisualNode } from '../types/visualization';

interface NameNodeNodeProps {
  node: VisualNode;
  fileCount: number;
  blockCount: number;
  isSelected?: boolean;
  onClick?: (node: VisualNode) => void;
}

export const NameNodeNode: React.FC<NameNodeNodeProps> = ({
  node,
  fileCount,
  blockCount,
  isSelected = false,
  onClick
}) => {
  const width = 150;
  const height = 82;
  const x = node.x - width / 2;
  const y = node.y - height / 2;

  const isHealthy = node.health === 'HEALTHY';

  return (
    <g
      transform={`translate(${x}, ${y})`}
      onClick={() => onClick && onClick(node)}
      style={{ cursor: 'pointer' }}
    >
      {/* Holographic Arc Outer Ring */}
      <circle
        cx={width / 2}
        cy={height / 2}
        r={height / 2 + 8}
        fill="none"
        stroke="rgba(0, 240, 255, 0.25)"
        strokeWidth="1"
        strokeDasharray="4 6"
        className="animate-spin"
        style={{ transformOrigin: `${width / 2}px ${height / 2}px`, animationDuration: '12s' }}
      />

      {/* Main Holographic Glass Card */}
      <rect
        width={width}
        height={height}
        rx={8}
        ry={8}
        fill="rgba(14, 21, 38, 0.92)"
        stroke={isSelected ? '#00f0ff' : 'rgba(0, 240, 255, 0.4)'}
        strokeWidth={isSelected ? 2 : 1}
        style={{ filter: 'drop-shadow(0 0 10px rgba(0, 240, 255, 0.2))' }}
      />

      {/* Corner Bracket Accents (JARVIS HUD Feel) */}
      <path d={`M 0,10 L 0,0 L 10,0`} fill="none" stroke="#00f0ff" strokeWidth="2" />
      <path d={`M ${width - 10},0 L ${width},0 L ${width},10`} fill="none" stroke="#00f0ff" strokeWidth="2" />
      <path d={`M 0,${height - 10} L 0,${height} L 10,${height}`} fill="none" stroke="#00f0ff" strokeWidth="2" />
      <path d={`M ${width - 10},${height} L ${width},${height} L ${width},${height - 10}`} fill="none" stroke="#00f0ff" strokeWidth="2" />

      {/* Status dot */}
      <circle cx={14} cy={14} r={4} fill={isHealthy ? '#22c55e' : '#ef4444'} />

      {/* Title */}
      <text
        x={24}
        y={18}
        fill="#ffffff"
        fontSize="11"
        fontWeight="800"
        fontFamily="'Space Grotesk', sans-serif"
        letterSpacing="0.5"
      >
        NAMENODE
      </text>

      <text
        x={width - 10}
        y={18}
        textAnchor="end"
        fill="#22c55e"
        fontSize="9"
        fontWeight="700"
        fontFamily="'JetBrains Mono', monospace"
      >
        {node.status}
      </text>

      {/* Metadata Row */}
      <g transform="translate(12, 38)">
        <text fill="#94a3b8" fontSize="10" fontFamily="'JetBrains Mono', monospace">
          Files: <tspan fill="#00f0ff" fontWeight="700">{fileCount}</tspan> | Blocks: <tspan fill="#00f0ff" fontWeight="700">{blockCount}</tspan>
        </text>

        <text y={18} fill="#64748b" fontSize="9" fontFamily="'JetBrains Mono', monospace">
          FsImage: <tspan fill="#22c55e">VALID</tspan> | EditLog: <tspan fill="#00f0ff">OPEN</tspan>
        </text>
      </g>
    </g>
  );
};
