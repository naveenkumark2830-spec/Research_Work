import React, { useState } from 'react';
import { VisualNode } from '../types/visualization';

interface DataNodeNodeProps {
  node: VisualNode;
  isSelected?: boolean;
  onClick?: (node: VisualNode) => void;
}

export const DataNodeNode: React.FC<DataNodeNodeProps> = ({
  node,
  isSelected = false,
  onClick
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const isExpanded = isHovered || isSelected;

  const width = isExpanded ? 135 : 110;
  const height = isExpanded ? 112 : 62;
  const x = node.x - width / 2;
  const y = node.y - height / 2;

  const isFailed = node.health === 'FAILED';
  const isDegraded = node.health === 'DEGRADED';

  const usedGb = (node.used_bytes / (1024 * 1024 * 1024)).toFixed(1);
  const totalGb = (node.capacity_bytes / (1024 * 1024 * 1024)).toFixed(0);
  const usagePct = node.capacity_bytes > 0
    ? Math.min(100, Math.round((node.used_bytes / node.capacity_bytes) * 100))
    : 0;

  const strokeColor = isFailed
    ? '#ef4444'
    : isDegraded
    ? '#f59e0b'
    : isExpanded
    ? '#00f0ff'
    : 'rgba(0, 240, 255, 0.3)';

  const statusDotColor = isFailed ? '#ef4444' : isDegraded ? '#f59e0b' : '#22c55e';

  return (
    <g
      transform={`translate(${x}, ${y})`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onClick && onClick(node)}
      style={{ cursor: 'pointer', transition: 'transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)' }}
    >
      {/* Pulse ring for healthy heartbeat */}
      {!isFailed && (
        <circle
          cx={width / 2}
          cy={0}
          r={10}
          fill="none"
          stroke="rgba(34, 197, 94, 0.35)"
          strokeWidth="1"
          className="animate-ping opacity-75"
        />
      )}

      {/* Main Container Card */}
      <rect
        width={width}
        height={height}
        rx={6}
        ry={6}
        fill="rgba(14, 21, 38, 0.94)"
        stroke={strokeColor}
        strokeWidth={isExpanded ? 1.5 : 1}
        style={{
          filter: isExpanded ? 'drop-shadow(0 0 12px rgba(0, 240, 255, 0.3))' : 'drop-shadow(0 0 6px rgba(0, 240, 255, 0.1))',
          transition: 'all 0.2s cubic-bezier(0.16, 1, 0.3, 1)'
        }}
      />

      {/* JARVIS Corner Accents */}
      <path d={`M 0,6 L 0,0 L 6,0`} fill="none" stroke={strokeColor} strokeWidth="1.5" />
      <path d={`M ${width - 6},0 L ${width},0 L ${width},6`} fill="none" stroke={strokeColor} strokeWidth="1.5" />
      <path d={`M 0,${height - 6} L 0,${height} L 6,${height}`} fill="none" stroke={strokeColor} strokeWidth="1.5" />
      <path d={`M ${width - 6},${height} L ${width},${height} L ${width},${height - 6}`} fill="none" stroke={strokeColor} strokeWidth="1.5" />

      {/* Heartbeat Status Dot */}
      <circle cx={12} cy={13} r={3.5} fill={statusDotColor} />

      {/* Title */}
      <text
        x={20}
        y={16}
        fill="#ffffff"
        fontSize="10"
        fontWeight="800"
        fontFamily="'Space Grotesk', sans-serif"
      >
        {node.label}
      </text>

      {!isExpanded ? (
        /* COLLAPSED DEFAULT VIEW: Storage % badge + block count badge */
        <g transform="translate(10, 28)">
          {/* Storage percentage badge */}
          <rect
            width="38"
            height="18"
            rx="4"
            fill="rgba(0, 240, 255, 0.12)"
            stroke="rgba(0, 240, 255, 0.3)"
            strokeWidth="0.8"
          />
          <text
            x="19"
            y="12"
            textAnchor="middle"
            fill="#00f0ff"
            fontSize="9"
            fontWeight="800"
            fontFamily="'JetBrains Mono', monospace"
          >
            {usagePct}%
          </text>

          {/* Block count single badge */}
          <rect
            x="44"
            width="46"
            height="18"
            rx="4"
            fill="rgba(34, 197, 94, 0.12)"
            stroke="rgba(34, 197, 94, 0.3)"
            strokeWidth="0.8"
          />
          <text
            x="67"
            y="12"
            textAnchor="middle"
            fill="#22c55e"
            fontSize="9"
            fontWeight="800"
            fontFamily="'JetBrains Mono', monospace"
          >
            {node.blocks.length} blks
          </text>
        </g>
      ) : (
        /* EXPANDED HOVER/CLICK VIEW: Full telemetry detail */
        <g>
          {/* Host subtext */}
          <text
            x={width / 2}
            y={32}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="8"
            fontFamily="'JetBrains Mono', monospace"
          >
            {node.hostname}
          </text>

          {/* Storage Capacity Detail */}
          <g transform="translate(8, 44)">
            <text fill="#94a3b8" fontSize="8" fontFamily="'JetBrains Mono', monospace">
              Storage: {usedGb}/{totalGb} GB ({usagePct}%)
            </text>
            <rect
              y={4}
              width={width - 16}
              height={4}
              rx={2}
              fill="#070a12"
              stroke="#1e2942"
              strokeWidth="0.5"
            />
            <rect
              y={4}
              width={Math.max(0, ((width - 16) * usagePct) / 100)}
              height={4}
              rx={2}
              fill={isFailed ? '#ef4444' : '#00f0ff'}
            />
          </g>

          {/* Individual Replicas Row */}
          <g transform="translate(8, 70)">
            <text fill="#94a3b8" fontSize="8" fontFamily="'JetBrains Mono', monospace">
              Replicas ({node.blocks.length}):
            </text>
            <g transform="translate(0, 6)">
              {node.blocks.slice(0, 4).map((blkId, idx) => (
                <rect
                  key={blkId}
                  x={idx * 26}
                  y={0}
                  width={22}
                  height={14}
                  rx={3}
                  fill={isFailed ? 'rgba(239, 68, 68, 0.2)' : 'rgba(0, 240, 255, 0.15)'}
                  stroke={isFailed ? '#ef4444' : 'rgba(0, 240, 255, 0.4)'}
                  strokeWidth="0.8"
                />
              ))}
              {node.blocks.slice(0, 4).map((blkId, idx) => (
                <text
                  key={`txt_${blkId}`}
                  x={idx * 26 + 11}
                  y={10}
                  textAnchor="middle"
                  fill="#00f0ff"
                  fontSize="8"
                  fontWeight="800"
                  fontFamily="'JetBrains Mono', monospace"
                >
                  B{idx + 1}
                </text>
              ))}
            </g>
          </g>
        </g>
      )}

      {/* Failure Overlay if Dead */}
      {isFailed && (
        <g transform={`translate(${width - 20}, ${height - 20})`}>
          <circle cx={8} cy={8} r={8} fill="#ef4444" stroke="#ffffff" strokeWidth="1" />
          <path d="M 5,5 L 11,11 M 11,5 L 5,11" stroke="#ffffff" strokeWidth="1.5" />
        </g>
      )}
    </g>
  );
};
