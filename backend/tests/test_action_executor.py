import pytest

from app.ai.action import IntentResult
from app.ai.executor import TeddyActionExecutor
from app.ai.intent import IntentType


class FakeHDFSService:

    async def create_file(
        self,
        file_size_mb,
        block_size_mb,
        replication_factor,
        datanode_count=None,
    ):
        return {
            "file_size_mb": file_size_mb,
            "block_size_mb": block_size_mb,
            "replication_factor": replication_factor,
            "datanode_count": datanode_count,
        }

    async def fail_datanode(self, node_id):
        return {
            "node_id": node_id,
            "status": "FAILED",
        }

    async def recover_datanode(self, node_id):
        return {
            "node_id": node_id,
            "status": "RECOVERED",
        }

    async def pause(self):
        return {
            "status": "PAUSED",
        }

    async def resume(self):
        return {
            "status": "RUNNING",
        }

    async def reset(self):
        return {
            "status": "RESET",
        }


@pytest.mark.asyncio
async def test_create_hdfs_file():

    service = FakeHDFSService()

    executor = TeddyActionExecutor(
        hdfs_service=service
    )

    intent = IntentResult(
        intent=IntentType.CREATE_HDFS_FILE,
        confidence=0.99,
        parameters={
            "file_size_mb": 1024,
            "block_size_mb": 128,
            "replication_factor": 3,
        },
    )

    result = await executor.execute(intent)

    assert result.success is True

    assert result.intent == IntentType.CREATE_HDFS_FILE

    assert result.data["file_size_mb"] == 1024

    assert result.data["block_size_mb"] == 128

    assert result.data["replication_factor"] == 3


@pytest.mark.asyncio
async def test_failure_action():

    service = FakeHDFSService()

    executor = TeddyActionExecutor(service)

    intent = IntentResult(
        intent=IntentType.SIMULATE_FAILURE,
        confidence=0.95,
        parameters={
            "node_id": "DataNode-3"
        },
    )

    result = await executor.execute(intent)

    assert result.success is True

    assert result.data["node_id"] == "DataNode-3"

    assert result.data["status"] == "FAILED"
