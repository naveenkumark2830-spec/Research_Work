from __future__ import annotations

from typing import Any

from app.services.hdfs_service import HDFSService
from app.simulation.hdfs.cluster import HDFSClusterConfig

from .action_validator import validate_simulation_action
from .schemas import SimulationAction


class TeddyActionExecutor:
    """
    Executes validated Teddy simulation actions against the
    real HDFS simulation service.
    """

    def __init__(self, hdfs_service: HDFSService):
        self.hdfs_service = hdfs_service

    def execute(
        self,
        session_id: str,
        action: SimulationAction,
        user_id: str | None = None,
    ):
        validated = validate_simulation_action(action)

        if validated.action == "none":
            return None

        if validated.action == "create_cluster":
            return self._create_cluster(
                session_id,
                validated.parameters,
                user_id,
            )

        if validated.action == "write_file":
            return self._write_file(
                session_id,
                validated.parameters,
                user_id,
            )

        if validated.action == "kill_datanode":
            node_id = validated.parameters["node_id"]

            return self.hdfs_service.kill_datanode(
                session_id=session_id,
                node_id=node_id,
                user_id=user_id,
            )

        if validated.action == "recover_datanode":
            node_id = validated.parameters["node_id"]

            return self.hdfs_service.recover_datanode(
                session_id=session_id,
                node_id=node_id,
                user_id=user_id,
            )

        if validated.action == "recover_under_replicated_blocks":
            return self.hdfs_service.recover_under_replicated_blocks(
                session_id=session_id,
                user_id=user_id,
            )

        raise ValueError(
            f"Unsupported Teddy action: {validated.action}"
        )

    def _create_cluster(
        self,
        session_id: str,
        parameters: dict[str, Any],
        user_id: str | None,
    ):
        block_bytes = parameters.get("block_size_bytes", 128 * 1024 ** 2)
        block_mb = max(1, min(1024, block_bytes // (1024 * 1024)))

        config = HDFSClusterConfig(
            block_size_bytes=block_bytes,
            block_size_mb=block_mb,
            replication_factor=parameters.get(
                "replication_factor",
                3,
            ),
            data_node_count=parameters.get(
                "data_node_count",
                5,
            ),
        )

        return self.hdfs_service.create_cluster(
            session_id=session_id,
            config=config,
            user_id=user_id,
        )

    def _write_file(
        self,
        session_id: str,
        parameters: dict[str, Any],
        user_id: str | None,
    ):
        block_bytes = parameters.get("block_size_bytes", 128 * 1024 ** 2)
        block_mb = max(1, min(1024, block_bytes // (1024 * 1024)))
        size_bytes = parameters.get("size_bytes", 500 * 1024 ** 2)
        file_mb = max(1, min(10240, size_bytes // (1024 * 1024)))

        # Configure the cluster first.
        config = HDFSClusterConfig(
            block_size_bytes=block_bytes,
            block_size_mb=block_mb,
            file_size_bytes=size_bytes,
            file_size_mb=file_mb,
            replication_factor=parameters.get(
                "replication_factor",
                3,
            ),
            data_node_count=parameters.get(
                "data_node_count",
                5,
            ),
        )

        self.hdfs_service.create_cluster(
            session_id=session_id,
            config=config,
            user_id=user_id,
        )

        # Then perform the actual file write.
        return self.hdfs_service.write_file(
            session_id=session_id,
            path=parameters["path"],
            size_bytes=parameters["size_bytes"],
            user_id=user_id,
        )
