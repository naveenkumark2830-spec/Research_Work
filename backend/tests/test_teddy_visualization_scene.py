import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.jarvis.schemas import TeddyRequest
from app.jarvis.provider import create_teddy_orchestrator
from app.jarvis.visualization_scene import build_visualization_scene
from app.simulation.hdfs.cluster import HDFSClusterConfig
from app.simulation.hdfs.engine import HDFSSimulationEngine


client = TestClient(app)


def test_build_visualization_scene_direct():
    config = HDFSClusterConfig(file_size_mb=1024, block_size_mb=128, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=config)
    engine.write_file("/test/data.bin", size_bytes=1024 * 1024 * 1024)
    cluster_state = engine.get_cluster_state()

    scene = build_visualization_scene(
        cluster_state,
        question="Show HDFS file blocks",
        teddy_response="File split into 8 blocks."
    )

    assert scene["scene_type"] == "hdfs"
    assert scene["question"] == "Show HDFS file blocks"
    assert len(scene["nodes"]) > 0
    assert len(scene["blocks"]) == 8
    assert scene["metadata"]["state_available"] is True
    assert scene["metadata"]["block_count"] == 8


@pytest.mark.asyncio
async def test_teddy_orchestrator_returns_visualization_scene():
    orchestrator = create_teddy_orchestrator()

    request = TeddyRequest(
        session_id="test-scene-session",
        user_id="test-user",
        message="What is the NameNode role in HDFS?",
    )

    response = await orchestrator.process(request)

    assert response.session_id == "test-scene-session"
    assert response.plan is not None
    assert hasattr(response, "visualization_scene")
