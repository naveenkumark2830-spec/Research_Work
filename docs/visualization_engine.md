# Level 5 — Dynamic HDFS Visualization Engine

## 1. Executive Summary

Level 5 implements the **Dynamic HDFS Visualization Engine** for the *AI-Assisted Interactive Hadoop Execution & Learning Simulator*. The visualization layer provides an interactive 2D SVG canvas depicting the authoritative backend HDFS cluster topology, DataNodes, NameNode metadata, block allocations, replication pipelines, and active node failures/recoveries.

---

## 2. Core Architecture & Principles

```
HDFS Simulation Engine (Level 3)
         │
         ▼
Event Engine & Cursor Playback (Level 4)
         │
         ▼
Timeline / Events API
         │
         ▼
Frontend Event & Cluster Reconciler (Level 5)
 ├── reconciler.ts (authoritative state parity)
 └── eventAdapter.ts (event-driven animation pulses)
         │
         ▼
2D SVG Cluster Canvas & Inspector
 ├── HDFSClusterView.tsx (SVG topology layout)
 ├── NameNodeNode.tsx (Active NN metadata & state)
 ├── DataNodeNode.tsx (Heartbeat ring, capacity, block replicas)
 ├── TransferAnimation.tsx (Pipeline & heartbeat SVG pulses)
 ├── FilePanel.tsx (Authoritative HDFS namespace listing)
 └── ComponentInspector.tsx (Deep metadata inspection panel)
```

### Key Architectural Principles
1. **Backend Authority**: The frontend visual layer NEVER invents simulation state or event order. All node counts, capacity usage, block states, and failure statuses stem directly from backend `HDFSClusterState` payloads.
2. **Deterministic Playback Sync**: Stepping, pausing, or restarting playback via Level 4 `EventCursor` automatically updates the visual canvas to mirror the precise sequence state.
3. **Decoupled Animation Engine**: Visual animations (data packet transfers, heartbeat pings) run on the UI rendering thread without distorting logical simulation clocks.

---

## 3. Package Structure (`frontend/src/visualization/`)

```
frontend/src/visualization/
├── types/
│   └── visualization.ts         # VisualNode, VisualBlock, VisualTransfer, InspectorTarget models
├── adapters/
│   └── eventAdapter.ts          # Processes Event stream into active transfer animations
├── utils/
│   └── reconciler.ts            # Pure state reconciler (HDFSClusterState -> VisualClusterState)
├── components/
│   ├── HDFSClusterView.tsx      # Main 2D SVG cluster topology canvas
│   ├── NameNodeNode.tsx         # SVG NameNode box with active state and metadata counts
│   ├── DataNodeNode.tsx         # SVG DataNode box with capacity bar, heartbeat pulse, and block badges
│   ├── HDFSBlockNode.tsx        # Color-coded block state icon/badge
│   ├── TransferAnimation.tsx    # SVG animated data packets along bezier path curves
│   ├── FilePanel.tsx            # HDFS File system listing table
│   └── ComponentInspector.tsx   # Inspection card for selected NameNode, DataNode, File, or Block
└── index.ts                     # Package exports
```

---

## 4. Visual Component Specifications

### 4.1 Topology Layout & Canvas (`HDFSClusterView.tsx`)
- **Canvas Size**: 1000x500 SVG viewBox.
- **Client Node**: Positioned at $(X=120, Y=100)$.
- **NameNode**: Positioned at $(X=500, Y=100)$.
- **DataNodes**: Positioned along horizontal rack line $(Y=380)$, evenly spaced across $X=150 \dots 850$.
- **Connection Lines**: Static dashed lines linking Client $\rightarrow$ NameNode and NameNode $\rightarrow$ DataNodes.

### 4.2 DataNode Representation (`DataNodeNode.tsx`)
- **Heartbeat Indicator**: Glowing green pulse ring for live healthy nodes; red cross overlay for dead/failed nodes.
- **Storage Bar**: Visual progress bar showing used storage vs total capacity (e.g., $100\text{ GB}$).
- **Block Badges**: Color-coded badges representing stored block replicas.

### 4.3 Active Transfer Animations (`TransferAnimation.tsx`)
- **Client Write**: Blue data pulse moving along curve from Client $\rightarrow$ Primary DataNode.
- **Replication Pipeline**: Amber data pulse moving along curve from Source DataNode $\rightarrow$ Target DataNode.
- **Heartbeat Ping**: Green dot moving from DataNode $\rightarrow$ NameNode.

### 4.4 Component Inspector (`ComponentInspector.tsx`)
Displays detailed properties when user selects a target in the UI:
- **NameNode**: EditLog/FSImage state, file & block counters, node ID.
- **DataNode**: Hostname, status (`LIVE`, `DEAD`), health (`HEALTHY`, `DEGRADED`, `FAILED`), capacity, stored block replica list.
- **File**: Path, size in MB, block size, replication factor, writing/closed status.
- **Block**: Block ID, desired vs actual replicas, health state (`WRITTEN`, `UNDER_REPLICATED`, `OVER_REPLICATED`, `CORRUPT`), replica locations.

---

## 5. Verification & Test Results

### Automated Backend Test Suite
- `python -m pytest`
- **Result**: `39 passed in 2.46s` (100% pass rate).

### Frontend Production Build
- `npx vite build`
- **Result**: Compiled cleanly in `1.75s` with 0 TypeScript/bundler errors.

---

## 6. Level 5 Approval Status

Level 5 is complete, fully verified, and ready for review.
