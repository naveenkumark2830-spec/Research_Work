from typing import Any, Dict, List


class VisualizationSceneBuilder:
    """
    Converts the current HDFS simulation state into frontend-neutral
    visualization instructions.

    This does NOT render anything.
    The frontend will later consume this scene.
    """

    def build_scene(
        self,
        hdfs_state: Any,
        *,
        question: str = "",
        teddy_response: str = "",
    ) -> Dict[str, Any]:

        nodes = []
        edges = []
        blocks = []
        events = []

        # ---------------------------------------------------------
        # Extract cluster information safely
        # ---------------------------------------------------------
        cluster = getattr(hdfs_state, "cluster", None)

        if cluster is None and isinstance(hdfs_state, dict):
            cluster = hdfs_state.get("cluster")

        if cluster is None:
            # Try extracting from SessionState object
            if hasattr(hdfs_state, "simulation") and hasattr(hdfs_state.simulation, "configuration"):
                custom_params = getattr(hdfs_state.simulation.configuration, "custom_parameters", {})
                if isinstance(custom_params, dict):
                    cluster_state = custom_params.get("hdfs_cluster_state", {})
                    if isinstance(cluster_state, dict):
                        cluster = cluster_state.get("cluster")
                    elif hasattr(cluster_state, "cluster"):
                        cluster = getattr(cluster_state, "cluster")
            elif isinstance(hdfs_state, dict):
                custom_params = hdfs_state.get("simulation", {}).get("configuration", {}).get("custom_parameters", {})
                if isinstance(custom_params, dict):
                    cluster_state = custom_params.get("hdfs_cluster_state", {})
                    if isinstance(cluster_state, dict):
                        cluster = cluster_state.get("cluster", cluster_state if "data_nodes" in cluster_state or "files" in cluster_state else None)

        if cluster is None and hdfs_state is not None:
            if hasattr(hdfs_state, "data_nodes") or hasattr(hdfs_state, "files") or (isinstance(hdfs_state, dict) and ("data_nodes" in hdfs_state or "files" in hdfs_state)):
                cluster = hdfs_state

        if cluster is None:
            return {
                "scene_type": "hdfs",
                "question": question,
                "teddy_response": teddy_response,
                "nodes": [],
                "edges": [],
                "blocks": [],
                "events": [],
                "metadata": {
                    "state_available": False,
                },
            }

        # ---------------------------------------------------------
        # NameNode
        # ---------------------------------------------------------
        nodes.append({
            "id": "namenode",
            "type": "namenode",
            "label": "NameNode",
            "status": "active",
            "role": "metadata",
        })

        # ---------------------------------------------------------
        # DataNodes
        # ---------------------------------------------------------
        datanodes = getattr(cluster, "data_nodes", None) or getattr(cluster, "datanodes", None)

        if datanodes is None and isinstance(cluster, dict):
            datanodes = cluster.get("data_nodes") or cluster.get("datanodes", [])

        if isinstance(datanodes, dict):
            datanodes = list(datanodes.values())

        datanodes = datanodes or []

        for index, datanode in enumerate(datanodes):

            if isinstance(datanode, dict):
                node_id = (
                    datanode.get("node_id")
                    or datanode.get("id")
                    or f"datanode-{index + 1}"
                )
                status = datanode.get("status", "active")
            else:
                node_id = (
                    getattr(datanode, "node_id", None)
                    or getattr(datanode, "id", None)
                    or f"datanode-{index + 1}"
                )
                status = getattr(datanode, "status", "active")

            nodes.append({
                "id": node_id,
                "type": "datanode",
                "label": node_id,
                "status": str(status),
                "role": "storage",
            })

            edges.append({
                "source": "namenode",
                "target": node_id,
                "type": "metadata",
            })

        # ---------------------------------------------------------
        # Files / blocks
        # ---------------------------------------------------------
        files = getattr(cluster, "files", None)

        if files is None and isinstance(cluster, dict):
            files = cluster.get("files", [])

        if isinstance(files, dict):
            files = list(files.values())

        files = files or []

        all_cluster_blocks = getattr(cluster, "blocks", None)
        if all_cluster_blocks is None and isinstance(cluster, dict):
            all_cluster_blocks = cluster.get("blocks")

        for file_index, file_data in enumerate(files):

            if isinstance(file_data, dict):
                path = file_data.get(
                    "path",
                    f"/file-{file_index + 1}"
                )
                file_blocks = file_data.get("blocks") or file_data.get("block_ids", [])
            else:
                path = getattr(
                    file_data,
                    "path",
                    f"/file-{file_index + 1}"
                )
                file_blocks = getattr(
                    file_data,
                    "blocks",
                    None
                ) or getattr(
                    file_data,
                    "block_ids",
                    []
                )

            if isinstance(file_blocks, dict):
                file_blocks = list(file_blocks.values())

            # Resolve block IDs to block objects if needed
            resolved_blocks = []
            for b in file_blocks:
                if isinstance(b, str) and all_cluster_blocks:
                    if isinstance(all_cluster_blocks, dict) and b in all_cluster_blocks:
                        resolved_blocks.append(all_cluster_blocks[b])
                    else:
                        resolved_blocks.append({"block_id": b})
                else:
                    resolved_blocks.append(b)

            file_blocks = resolved_blocks

            file_node_id = f"file-{file_index + 1}"

            nodes.append({
                "id": file_node_id,
                "type": "file",
                "label": path,
                "status": "stored",
            })

            for block_index, block in enumerate(file_blocks):

                if isinstance(block, dict):
                    block_id = (
                        block.get("block_id")
                        or block.get("id")
                        or f"block-{file_index + 1}-{block_index + 1}"
                    )
                    replicas = (
                        block.get("replicas")
                        or block.get("replica_nodes")
                        or block.get("data_nodes")
                        or []
                    )
                else:
                    block_id = (
                        getattr(block, "block_id", None)
                        or getattr(block, "id", None)
                        or f"block-{file_index + 1}-{block_index + 1}"
                    )
                    replicas = (
                        getattr(block, "replicas", None)
                        or getattr(block, "replica_nodes", None)
                        or getattr(block, "data_nodes", None)
                        or []
                    )

                blocks.append({
                    "id": block_id,
                    "file": path,
                    "replicas": list(replicas),
                })

                nodes.append({
                    "id": block_id,
                    "type": "block",
                    "label": block_id,
                    "status": "stored",
                })

                edges.append({
                    "source": file_node_id,
                    "target": block_id,
                    "type": "contains",
                })

                for replica in replicas:
                    replica_id = (
                        replica
                        if isinstance(replica, str)
                        else getattr(
                            replica,
                            "node_id",
                            None
                        )
                    )

                    if replica_id:
                        edges.append({
                            "source": block_id,
                            "target": replica_id,
                            "type": "replica",
                        })

        # ---------------------------------------------------------
        # Determine scene events
        # ---------------------------------------------------------
        active_nodes = [
            node for node in nodes
            if node["type"] == "datanode"
            and str(node["status"]).lower() in {
                "active",
                "healthy",
                "running",
                "alive",
            }
        ]

        failed_nodes = [
            node for node in nodes
            if node["type"] == "datanode"
            and str(node["status"]).lower() in {
                "failed",
                "dead",
                "offline",
                "down",
            }
        ]

        if failed_nodes:
            events.append({
                "type": "datanode_failure",
                "nodes": [node["id"] for node in failed_nodes],
            })

        if blocks:
            events.append({
                "type": "block_distribution",
                "block_count": len(blocks),
                "active_datanodes": len(active_nodes),
            })

        return {
            "scene_type": "hdfs",
            "question": question,
            "teddy_response": teddy_response,
            "nodes": nodes,
            "edges": edges,
            "blocks": blocks,
            "events": events,
            "metadata": {
                "state_available": True,
                "datanode_count": len(datanodes),
                "active_datanode_count": len(active_nodes),
                "failed_datanode_count": len(failed_nodes),
                "block_count": len(blocks),
            },
        }


def build_visualization_scene(
    hdfs_state: Any,
    *,
    question: str = "",
    teddy_response: str = "",
) -> Dict[str, Any]:
    return VisualizationSceneBuilder().build_scene(
        hdfs_state,
        question=question,
        teddy_response=teddy_response,
    )
