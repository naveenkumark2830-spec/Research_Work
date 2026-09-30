from typing import Any, Dict, List


class VisualizationAnimationBuilder:
    """
    Converts an HDFS action + before/after visualization scenes
    into frontend-neutral animation instructions.
    """

    def build_animation(
        self,
        action: str,
        before_scene: Dict[str, Any],
        after_scene: Dict[str, Any],
    ) -> Dict[str, Any]:

        animations: List[Dict[str, Any]] = []

        action = action.lower().strip()

        if action == "write_file":
            animations.extend(
                self._write_file_animation(
                    before_scene,
                    after_scene,
                )
            )

        elif action == "kill_datanode":
            animations.extend(
                self._failure_animation(
                    before_scene,
                    after_scene,
                )
            )

        elif action == "recover_datanode":
            animations.extend(
                self._recovery_animation(
                    before_scene,
                    after_scene,
                )
            )

        elif action == "recover_under_replicated_blocks":
            animations.extend(
                self._replication_recovery_animation(
                    before_scene,
                    after_scene,
                )
            )

        return {
            "animation_type": "hdfs",
            "action": action,
            "animations": animations,
            "metadata": {
                "animation_count": len(animations),
            },
        }

    # ---------------------------------------------------------
    # FILE WRITE
    # ---------------------------------------------------------

    def _write_file_animation(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        animations = []

        before_blocks = {
            block["id"]
            for block in before.get("blocks", [])
        }

        new_blocks = [
            block
            for block in after.get("blocks", [])
            if block["id"] not in before_blocks
        ]

        for block in new_blocks:

            animations.append({
                "type": "block_created",
                "target": block["id"],
                "duration_ms": 600,
            })

            for replica_index, datanode in enumerate(
                block.get("replicas", [])
            ):
                animations.append({
                    "type": "replication",
                    "block": block["id"],
                    "source": (
                        "client"
                        if replica_index == 0
                        else block["replicas"][replica_index - 1]
                    ),
                    "target": datanode,
                    "duration_ms": 700,
                    "sequence": replica_index + 1,
                })

        if new_blocks:
            animations.append({
                "type": "operation_complete",
                "operation": "write_file",
                "duration_ms": 400,
            })

        return animations

    # ---------------------------------------------------------
    # DATANODE FAILURE
    # ---------------------------------------------------------

    def _failure_animation(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        before_nodes = {
            node["id"]: node
            for node in before.get("nodes", [])
            if node.get("type") == "datanode"
        }

        after_nodes = {
            node["id"]: node
            for node in after.get("nodes", [])
            if node.get("type") == "datanode"
        }

        animations = []

        for node_id, after_node in after_nodes.items():

            before_node = before_nodes.get(node_id)

            if not before_node:
                continue

            before_status = str(
                before_node.get("status", "")
            ).lower()

            after_status = str(
                after_node.get("status", "")
            ).lower()

            if (
                before_status not in {"failed", "dead", "offline", "down"}
                and after_status in {"failed", "dead", "offline", "down"}
            ):
                animations.append({
                    "type": "datanode_failure",
                    "target": node_id,
                    "duration_ms": 800,
                })

        return animations

    # ---------------------------------------------------------
    # DATANODE RECOVERY
    # ---------------------------------------------------------

    def _recovery_animation(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        before_nodes = {
            node["id"]: node
            for node in before.get("nodes", [])
            if node.get("type") == "datanode"
        }

        after_nodes = {
            node["id"]: node
            for node in after.get("nodes", [])
            if node.get("type") == "datanode"
        }

        animations = []

        for node_id, after_node in after_nodes.items():

            before_node = before_nodes.get(node_id)

            if not before_node:
                continue

            before_status = str(
                before_node.get("status", "")
            ).lower()

            after_status = str(
                after_node.get("status", "")
            ).lower()

            if (
                before_status in {"failed", "dead", "offline", "down"}
                and after_status in {
                    "active",
                    "healthy",
                    "running",
                    "alive",
                }
            ):
                animations.append({
                    "type": "datanode_recovery",
                    "target": node_id,
                    "duration_ms": 800,
                })

        return animations

    # ---------------------------------------------------------
    # REPLICATION RECOVERY
    # ---------------------------------------------------------

    def _replication_recovery_animation(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any],
    ) -> List[Dict[str, Any]]:

        animations = []

        before_blocks = {
            block["id"]: block
            for block in before.get("blocks", [])
        }

        after_blocks = {
            block["id"]: block
            for block in after.get("blocks", [])
        }

        for block_id, after_block in after_blocks.items():

            before_block = before_blocks.get(block_id)

            if not before_block:
                continue

            before_replicas = set(
                before_block.get("replicas", [])
            )

            after_replicas = set(
                after_block.get("replicas", [])
            )

            new_replicas = after_replicas - before_replicas

            for datanode in new_replicas:
                animations.append({
                    "type": "block_replication_recovery",
                    "block": block_id,
                    "target": datanode,
                    "duration_ms": 700,
                })

        return animations


def build_animation(
    action: str,
    before_scene: Dict[str, Any],
    after_scene: Dict[str, Any],
) -> Dict[str, Any]:

    return VisualizationAnimationBuilder().build_animation(
        action,
        before_scene,
        after_scene,
    )
