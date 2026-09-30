from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from typing import Any, Optional

from app.simulation.hdfs.cluster import HDFSClusterConfig
from .action import IntentResult
from .exceptions import InvalidAIActionError
from .intent import IntentType


@dataclass
class ExecutionResult:
    success: bool
    intent: IntentType
    message: str
    data: dict[str, Any]


class TeddyActionExecutor:
    """
    Converts validated Teddy intents into real HDFS simulation operations.

    LLM/NLU decides WHAT the user wants.
    This executor decides HOW to safely execute it.
    """

    def __init__(self, hdfs_service: Any):
        self.hdfs_service = hdfs_service

    async def execute(
        self,
        result: IntentResult,
        *,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> ExecutionResult:

        intent = result.intent

        if intent == IntentType.CREATE_HDFS_FILE:
            return await self._create_hdfs_file(
                result,
                session_id=session_id,
                user_id=user_id,
            )

        if intent == IntentType.SIMULATE_FAILURE:
            return await self._fail_datanode(
                result,
                session_id=session_id,
                user_id=user_id,
            )

        if intent == IntentType.RECOVER_DATANODE:
            return await self._recover(
                result,
                session_id=session_id,
                user_id=user_id,
            )

        if intent == IntentType.PAUSE_SIMULATION:
            return await self._pause(result, session_id=session_id, user_id=user_id)

        if intent == IntentType.RESUME_SIMULATION:
            return await self._resume(result, session_id=session_id, user_id=user_id)

        if intent == IntentType.RESET_SIMULATION:
            return await self._reset(result, session_id=session_id, user_id=user_id)

        if intent in {
            IntentType.EXPLAIN_HDFS,
            IntentType.EXPLAIN_COMPONENT,
            IntentType.EXPLAIN_BLOCKS,
            IntentType.EXPLAIN_REPLICATION,
        }:
            return ExecutionResult(
                success=True,
                intent=result.intent,
                message="Explanation request requires the Teddy explanation layer.",
                data=result.parameters,
            )

        raise InvalidAIActionError(
            f"Unsupported executable intent: {intent.value}"
        )

    async def _invoke_service_method(self, method_name: str, *args, **kwargs) -> Any:
        """Helper to invoke synchronous or asynchronous HDFSService methods."""
        method = getattr(self.hdfs_service, method_name)
        if inspect.iscoroutinefunction(method):
            return await method(*args, **kwargs)
        else:
            return await asyncio.to_thread(method, *args, **kwargs)

    async def _create_hdfs_file(
        self,
        result: IntentResult,
        *,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> ExecutionResult:

        params = result.parameters

        file_size_mb = int(params["file_size_mb"])
        block_size_mb = int(params["block_size_mb"])
        replication_factor = int(params["replication_factor"])
        datanode_count = int(params.get("datanode_count", 5))

        file_size_bytes = file_size_mb * 1024 * 1024

        # Check if caller passed session_id for real HDFSService integration
        if session_id and hasattr(self.hdfs_service, "create_cluster"):
            cluster_config = HDFSClusterConfig(
                file_size_mb=file_size_mb,
                block_size_mb=block_size_mb,
                replication_factor=replication_factor,
                data_node_count=datanode_count,
            )
            cluster_state = await self._invoke_service_method(
                "create_cluster",
                session_id=session_id,
                config=cluster_config,
                user_id=user_id,
            )

            write_result = await self._invoke_service_method(
                "write_file",
                session_id=session_id,
                path="/teddy/input/data.bin",
                size_bytes=file_size_bytes,
                user_id=user_id,
            )

            state = cluster_state
            if hasattr(self.hdfs_service, "get_hdfs_cluster_state"):
                state = await self._invoke_service_method(
                    "get_hdfs_cluster_state",
                    session_id=session_id,
                    user_id=user_id,
                )

            return ExecutionResult(
                success=True,
                intent=result.intent,
                message=(
                    f"Created {file_size_mb} MB HDFS file "
                    f"with {block_size_mb} MB blocks and "
                    f"replication factor {replication_factor}."
                ),
                data={
                    "cluster": cluster_state,
                    "write": write_result,
                    "state": state,
                    "file_size_mb": file_size_mb,
                    "block_size_mb": block_size_mb,
                    "replication_factor": replication_factor,
                },
            )

        # Fallback / Mock service method signature support for standalone unit tests
        simulation_result = await self._invoke_service_method(
            "create_file",
            file_size_mb=file_size_mb,
            block_size_mb=block_size_mb,
            replication_factor=replication_factor,
            datanode_count=datanode_count,
        )

        return ExecutionResult(
            success=True,
            intent=result.intent,
            message="HDFS file simulation created successfully.",
            data=simulation_result,
        )

    async def _fail_datanode(
        self,
        result: IntentResult,
        *,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> ExecutionResult:

        node_id = result.parameters.get("node_id") or result.parameters.get("component")

        if session_id and hasattr(self.hdfs_service, "kill_datanode"):
            failure_result = await self._invoke_service_method(
                "kill_datanode",
                session_id=session_id,
                node_id=node_id,
                user_id=user_id,
            )
            state = failure_result
            if hasattr(self.hdfs_service, "get_hdfs_cluster_state"):
                state = await self._invoke_service_method(
                    "get_hdfs_cluster_state",
                    session_id=session_id,
                    user_id=user_id,
                )
            return ExecutionResult(
                success=True,
                intent=result.intent,
                message=f"{node_id} has been failed.",
                data={
                    "failure": failure_result,
                    "state": state,
                    "node_id": node_id,
                    "status": "FAILED",
                },
            )

        simulation_result = await self._invoke_service_method(
            "fail_datanode",
            node_id=node_id,
        )

        return ExecutionResult(
            success=True,
            intent=result.intent,
            message=f"{node_id} failure simulated.",
            data=simulation_result,
        )

    async def _recover(
        self,
        result: IntentResult,
        *,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> ExecutionResult:

        node_id = result.parameters.get("node_id")

        if session_id and hasattr(self.hdfs_service, "recover_datanode"):
            if node_id:
                recovery_result = await self._invoke_service_method(
                    "recover_datanode",
                    session_id=session_id,
                    node_id=node_id,
                    user_id=user_id,
                )
            else:
                recovery_result = await self._invoke_service_method(
                    "recover_under_replicated_blocks",
                    session_id=session_id,
                    user_id=user_id,
                )
            state = recovery_result
            if hasattr(self.hdfs_service, "get_hdfs_cluster_state"):
                state = await self._invoke_service_method(
                    "get_hdfs_cluster_state",
                    session_id=session_id,
                    user_id=user_id,
                )
            return ExecutionResult(
                success=True,
                intent=result.intent,
                message="HDFS recovery completed.",
                data={
                    "recovery": recovery_result,
                    "state": state,
                },
            )

        simulation_result = await self._invoke_service_method(
            "recover_datanode",
            node_id=node_id,
        )

        return ExecutionResult(
            success=True,
            intent=result.intent,
            message=f"{node_id} recovery triggered.",
            data=simulation_result,
        )

    async def _pause(self, result: IntentResult, session_id: Optional[str] = None, user_id: Optional[str] = None) -> ExecutionResult:
        if session_id and hasattr(self.hdfs_service, "pause_simulation"):
            res = await self._invoke_service_method("pause_simulation", session_id=session_id, user_id=user_id)
            return ExecutionResult(success=True, intent=result.intent, message="Simulation paused.", data={"state": res})

        if hasattr(self.hdfs_service, "pause"):
            simulation_result = await self._invoke_service_method("pause")
            return ExecutionResult(success=True, intent=result.intent, message="Simulation paused.", data=simulation_result)

        return ExecutionResult(success=True, intent=result.intent, message="Simulation paused.", data={})

    async def _resume(self, result: IntentResult, session_id: Optional[str] = None, user_id: Optional[str] = None) -> ExecutionResult:
        if session_id and hasattr(self.hdfs_service, "resume_simulation"):
            res = await self._invoke_service_method("resume_simulation", session_id=session_id, user_id=user_id)
            return ExecutionResult(success=True, intent=result.intent, message="Simulation resumed.", data={"state": res})

        if hasattr(self.hdfs_service, "resume"):
            simulation_result = await self._invoke_service_method("resume")
            return ExecutionResult(success=True, intent=result.intent, message="Simulation resumed.", data=simulation_result)

        return ExecutionResult(success=True, intent=result.intent, message="Simulation resumed.", data={})

    async def _reset(self, result: IntentResult, session_id: Optional[str] = None, user_id: Optional[str] = None) -> ExecutionResult:
        if session_id and hasattr(self.hdfs_service, "restart_simulation"):
            res = await self._invoke_service_method("restart_simulation", session_id=session_id, user_id=user_id)
            return ExecutionResult(success=True, intent=result.intent, message="Simulation reset.", data={"state": res})

        if hasattr(self.hdfs_service, "reset"):
            simulation_result = await self._invoke_service_method("reset")
            return ExecutionResult(success=True, intent=result.intent, message="Simulation reset.", data=simulation_result)

        return ExecutionResult(success=True, intent=result.intent, message="Simulation reset.", data={})
