# HDFS Deterministic Simulation Engine Specification & Architecture

## Overview
The **HDFS Simulation Engine** is a pure Python, deterministic distributed system simulator for the Hadoop Distributed File System (HDFS). It operates as the source of truth for HDFS behaviors within the **AI-Assisted Interactive Hadoop Execution & Learning Simulator**.

It is completely decoupled from FastAPI, React, real Hadoop clusters, network IO, or non-deterministic sources (such as wall-clock timing or `random` number generators).

---

## Core Principles & Determinism
1. **Deterministic State Transitions**: Identical configuration + identical inputs produce 100% identical block counts, block sizes, DataNode placements, logical event sequences, and cluster metadata.
2. **Logical Simulation Clock**: Replaces real-time `time.sleep()` with a monotonic `SimulationClock` (`simulation_time`), advancing explicitly on simulation events.
3. **Structured Event Stream**: Produces fine-grained, structured domain events (`HDFSEventType`) describing system mutations for auditing, state tracking, and future visualization.

---

## Architectural Components

### 1. NameNode (`app.simulation.hdfs.namenode`)
- **Metadata Registry**: Maintains mapping of file paths to blocks, block replica locations across DataNodes, cluster membership, under-replicated block lists, and lost block lists.
- **Zero Storage Payload**: Stores metadata only; does NOT store file content bytes.
- **Location Lookup**: Responds to queries (`get_block_locations`, `get_file_blocks`) without querying DataNode contents.

### 2. DataNodes (`app.simulation.hdfs.datanode`)
- Represents logical storage nodes (`datanode-1` ... `datanode-N`).
- Tracks capacity, used bytes, available bytes, stored block IDs, status (`LIVE`, `FAILED`, `DECOMMISSIONED`), and heartbeat health (`HEALTHY`, `MISSED`).

### 3. Block Calculation & Allocation (`app.simulation.hdfs.block`)
- **Block Count Formula**: $\text{block\_count} = \lceil \frac{\text{file\_size}}{\text{block\_size}} \rceil$.
- **Exact Size Distribution**: Calculates exact byte distribution (e.g. 500 MB file with 128 MB block size yields 3 blocks of 128 MB and 1 block of 116 MB).

### 4. Deterministic Placement & Replication (`app.simulation.hdfs.placement`, `replication`)
- **Round-Robin Placement**: Places block replicas across LIVE DataNodes using index-offset round-robin selection.
- **Unique Placement Constraint**: Enforces no duplicate replicas exist on the same DataNode (`len(set(replica_nodes)) == replication_factor`).
- **Replication States**:
  - `HEALTHY`: $\text{actual\_healthy\_replicas} \ge \text{desired\_replication}$
  - `UNDER_REPLICATED`: $0 < \text{actual\_healthy\_replicas} < \text{desired\_replication}$
  - `LOST`: $\text{actual\_healthy\_replicas} == 0$

### 5. Failure & Recovery Engine (`app.simulation.hdfs.failure`, `recovery`)
- **DataNode Failure**: Marks node `FAILED`, removes node from active replica sets, recalculates block replication health, and flags under-replicated/lost blocks.
- **Re-Replication Recovery**: Identifies under-replicated blocks, deterministically selects healthy replacement DataNodes excluding current replica locations, creates replacement replicas, updates NameNode metadata, and restores block state to `HEALTHY`.
- **Actual Data Loss**: If all replica nodes for a block fail, the block transitions to `LOST`. File read requests attempt to access `LOST` blocks raise a `BlockDataLossError`.

---

## REST API Endpoints (`/api/v1/simulation/hdfs`)
- `POST /cluster`: Initialize session HDFS cluster.
- `POST /sessions/{session_id}/write`: Execute file write pipeline.
- `POST /sessions/{session_id}/read`: Execute file read pipeline.
- `POST /sessions/{session_id}/datanodes/{node_id}/fail`: Inject DataNode failure.
- `POST /sessions/{session_id}/recover`: Trigger under-replication recovery.
- `GET /sessions/{session_id}/state`: Retrieve full `HDFSClusterState`.

---

## Session Isolation
Every session owns an independent `HDFSClusterState` instance stored in the session state repository. Operations on Session A do not affect Session B.
