import React from 'react';
import {
  VisualClusterState,
  VisualNode,
  InspectorTarget
} from '../types/visualization';
import { NameNodeNode } from './NameNodeNode';
import { DataNodeNode } from './DataNodeNode';
import { TransferAnimation } from './TransferAnimation';

interface HDFSClusterViewProps {
  clusterState: VisualClusterState;
  onSelectTarget: (target: InspectorTarget) => void;
  selectedTarget: InspectorTarget | null;
}

export const HDFSClusterView: React.FC<HDFSClusterViewProps> = ({
  clusterState,
  onSelectTarget,
  selectedTarget
}) => {
  const {
    nodes = {},
    transfers = []
  } = clusterState || {};

  const nodesList: any[] = Array.isArray(nodes)
    ? nodes
    : Object.values(nodes || {});

  const hasClient = nodesList.some((n) => String(n.type).toUpperCase() === 'CLIENT');
  const clientNode: VisualNode | null = hasClient ? {
    id: 'client-0',
    type: 'CLIENT' as const,
    label: 'DFS Client',
    hostname: 'client.hadoop.local',
    status: 'READY',
    health: 'HEALTHY' as const,
    x: 120,
    y: 90,
    capacity_bytes: 0,
    used_bytes: 0,
    blocks: []
  } : null;

  const rawNameNode = nodesList.find((n) => String(n.type).toUpperCase() === 'NAMENODE');
  const nameNode: VisualNode | null = rawNameNode ? {
    id: rawNameNode.id || 'namenode-1',
    type: 'NAMENODE' as const,
    label: rawNameNode.label || 'Active NameNode',
    hostname: rawNameNode.hostname || 'nn1.hadoop.local',
    status: String(rawNameNode.status || 'ACTIVE').toUpperCase(),
    health: (['HEALTHY', 'DEGRADED', 'FAILED'].includes(String(rawNameNode.health).toUpperCase()) ? String(rawNameNode.health).toUpperCase() : 'HEALTHY') as any,
    x: rawNameNode.x ?? 500,
    y: rawNameNode.y ?? 90,
    capacity_bytes: rawNameNode.capacity_bytes || 0,
    used_bytes: rawNameNode.used_bytes || 0,
    blocks: rawNameNode.blocks || []
  } : null;

  const rawDataNodes = nodesList.filter((n) => String(n.type).toUpperCase() === 'DATANODE');

  const dataNodes: VisualNode[] = rawDataNodes.map((dn, idx) => ({
    id: dn.id || `datanode-${idx + 1}`,
    type: 'DATANODE' as const,
    label: dn.label || `DataNode-${idx + 1}`,
    hostname: dn.hostname || `dn${idx + 1}.hadoop.local`,
    status: String(dn.status || 'LIVE').toUpperCase(),
    health: (['HEALTHY', 'DEGRADED', 'FAILED'].includes(String(dn.health).toUpperCase()) ? String(dn.health).toUpperCase() : 'HEALTHY') as any,
    x: dn.x ?? (160 + idx * 165),
    y: dn.y ?? 340,
    capacity_bytes: dn.capacity_bytes || 100 * 1024 * 1024 * 1024,
    used_bytes: dn.used_bytes || 20 * 1024 * 1024 * 1024,
    blocks: dn.blocks || []
  }));




  return (
    <div style={{
      width: '100%',
      height: '100%',
      backgroundColor: '#070a12',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <svg
        viewBox="0 0 1000 520"
        preserveAspectRatio="xMidYMid meet"
        style={{
          width: '100%',
          height: '100%',
          userSelect: 'none',
          backgroundColor: '#070a12'
        }}
      >
        {/* Futuristic Laser Grid Pattern */}
        <defs>
          <pattern
            id="hud-grid"
            width="50"
            height="50"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 50 0 L 0 0 0 50"
              fill="none"
              stroke="rgba(0, 240, 255, 0.05)"
              strokeWidth="1"
            />
            <circle cx="0" cy="0" r="1.5" fill="rgba(0, 240, 255, 0.2)" />
          </pattern>
        </defs>
        <rect width="1000" height="520" fill="url(#hud-grid)" />

        {/* JARVIS Canvas Reticle Target Corners */}
        <g stroke="rgba(0, 240, 255, 0.3)" strokeWidth="1.5" fill="none">
          <path d="M 20,40 L 20,20 L 40,20" />
          <path d="M 980,40 L 980,20 L 960,20" />
          <path d="M 20,480 L 20,500 L 40,500" />
          <path d="M 980,480 L 980,500 L 960,500" />
        </g>

        {/* Topology Rack Boundary */}
        <rect
          x="60"
          y="260"
          width="880"
          height="170"
          rx="10"
          fill="rgba(14, 21, 38, 0.4)"
          stroke="rgba(0, 240, 255, 0.25)"
          strokeWidth="1"
          strokeDasharray="4 4"
        />
        <text
          x="75"
          y="280"
          fill="#64748b"
          fontSize="10"
          fontWeight="700"
          fontFamily="'JetBrains Mono', monospace"
          letterSpacing="0.5"
        >
          [ STORAGE RACK /default-rack ]
        </text>

        {/* Connection Lines: Client -> NameNode */}
        {nameNode && clientNode && (
          <line
            x1={clientNode.x + 35}
            y1={clientNode.y}
            x2={nameNode.x - 75}
            y2={nameNode.y}
            stroke="rgba(0, 240, 255, 0.4)"
            strokeWidth="1.5"
            strokeDasharray="4 4"
          />
        )}

        {/* Connection Lines: NameNode -> DataNodes */}
        {nameNode &&
          dataNodes.map((dn) => (
            <line
              key={`line_nn_${dn.id}`}
              x1={nameNode.x}
              y1={nameNode.y + 40}
              x2={dn.x}
              y2={dn.y - 50}
              stroke="rgba(30, 41, 66, 0.8)"
              strokeWidth="1.5"
            />
          ))}

        {/* Active Data Transfer Animations */}
        {transfers.map((tr) => (
          <TransferAnimation key={tr.id} transfer={tr} nodes={nodes} />
        ))}

        {/* Render DFS Client Node */}
        {clientNode && (
          <g
            transform={`translate(${clientNode.x - 45}, ${clientNode.y - 28})`}
            style={{ cursor: 'pointer' }}
          >
            <rect
              width="90"
              height="56"
              rx={8}
              fill="rgba(14, 21, 38, 0.92)"
              stroke="#00f0ff"
              strokeWidth="1.5"
              style={{ filter: 'drop-shadow(0 0 8px rgba(0, 240, 255, 0.2))' }}
            />
            <path d="M 0,6 L 0,0 L 6,0" fill="none" stroke="#00f0ff" strokeWidth="1.5" />
            <path d="M 84,0 L 90,0 L 90,6" fill="none" stroke="#00f0ff" strokeWidth="1.5" />
            <text
              x="45"
              y="25"
              textAnchor="middle"
              fill="#00f0ff"
              fontSize="11"
              fontWeight="800"
              fontFamily="'Space Grotesk', sans-serif"
            >
              DFS CLIENT
            </text>
            <text
              x="45"
              y="41"
              textAnchor="middle"
              fill="#94a3b8"
              fontSize="9"
              fontFamily="'JetBrains Mono', monospace"
            >
              Pipeline Stream
            </text>
          </g>
        )}

        {/* Render NameNode */}
        {nameNode && (
          <NameNodeNode
            node={{ ...nameNode, y: 90 }}
            fileCount={1}
            blockCount={2}
            isSelected={
              selectedTarget?.type === 'NAMENODE' &&
              selectedTarget?.id === nameNode.id
            }
            onClick={(nn) =>
              onSelectTarget({
                type: 'NAMENODE',
                id: nn.id,
                data: nn
              })
            }
          />
        )}

        {/* Render DataNodes */}
        {dataNodes.map((dn) => (
          <DataNodeNode
            key={dn.id}
            node={{ ...dn, y: 340 }}
            isSelected={
              selectedTarget?.type === 'DATANODE' &&
              selectedTarget?.id === dn.id
            }
            onClick={(dNode) =>
              onSelectTarget({
                type: 'DATANODE',
                id: dNode.id,
                data: dNode
              })
            }
          />
        ))}
      </svg>
    </div>
  );
};
