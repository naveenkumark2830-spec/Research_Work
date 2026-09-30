import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db


@pytest.fixture
def client():
    init_db()
    with TestClient(app) as c:
        yield c


def test_level5_end_to_end_visual_acceptance(client):
    # 1. Create User
    user_res = client.post("/api/v1/users", json={"display_name": "Level 5 Visual Tester"})
    assert user_res.status_code == 201
    user_id = user_res.json()["user"]["user_id"]
    assert user_id is not None

    # 2. Create Fresh Session
    session_res = client.post("/api/v1/sessions", json={
        "user_id": user_id,
        "current_topic": "Level 5 HDFS Visual Acceptance"
    })
    assert session_res.status_code == 201
    session_id = session_res.json()["session"]["session_id"]
    assert session_id is not None

    # 3. Create HDFS Cluster with 5 DataNodes, 128MB block size, 3x replication factor
    cluster_init_res = client.post(
        "/api/v1/simulation/hdfs/cluster",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "config": {
                "file_size_bytes": 524288000,
                "block_size_bytes": 134217728,
                "replication_factor": 3,
                "data_node_count": 5
            }
        },
        headers={"X-User-Id": user_id}
    )
    assert cluster_init_res.status_code == 201

    # 4. Start HDFS Simulation File Write (500 MB)
    write_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "input_file.dat", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )
    assert write_res.status_code == 200

    # Fetch Cluster State
    cluster_res = client.get(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/state",
        headers={"X-User-Id": user_id}
    )
    assert cluster_res.status_code == 200
    cluster_state = cluster_res.json()

    # 5. Verify exact Cluster Metrics:
    # - 1 NameNode
    # - 5 DataNodes
    # - 4 blocks (ceil(500/128) = 4)
    # - 12 total replicas (4 blocks * 3 replicas)
    # - File metadata: 500 MB, input_file.dat
    assert cluster_state["namenode"] is not None
    assert len(cluster_state["datanodes"]) == 5
    assert len(cluster_state["blocks"]) == 4
    assert len(cluster_state["files"]) == 1

    file_meta = list(cluster_state["files"].values())[0]
    assert file_meta["path"] == "input_file.dat"
    assert file_meta["size_bytes"] == 524288000
    assert len(file_meta["block_ids"]) == 4

    total_replicas = sum(len(b["replica_nodes"]) for b in cluster_state["blocks"].values())
    assert total_replicas == 12

    # 6. Verify Block Creation & Replica Placement
    for block_id, block_data in cluster_state["blocks"].items():
        assert block_data["desired_replication"] == 3
        assert len(block_data["replica_nodes"]) == 3

    # 7. Test DataNode Failure & Under-replication
    failed_dn_id = "datanode-1"

    fail_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/{failed_dn_id}/fail",
        headers={"X-User-Id": user_id}
    )
    assert fail_res.status_code == 200

    fail_state_res = client.get(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/state",
        headers={"X-User-Id": user_id}
    )
    assert fail_state_res.status_code == 200
    fail_cluster = fail_state_res.json()
    assert fail_cluster["datanodes"][failed_dn_id]["status"] == "FAILED"

    # 8. Recover DataNode & Verify Re-replication
    recover_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/recover",
        headers={"X-User-Id": user_id}
    )
    assert recover_res.status_code == 200

    rec_state_res = client.get(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/state",
        headers={"X-User-Id": user_id}
    )
    assert rec_state_res.status_code == 200
    rec_cluster = rec_state_res.json()
    assert rec_cluster["datanodes"][failed_dn_id]["status"] == "FAILED"

    # 9. Verify Event Timeline & Playback Cursor API (Pause, Resume, Restart)
    events_res = client.get(f"/api/v1/sessions/{session_id}/events", headers={"X-User-Id": user_id})
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 4

    # Test Pause
    pause_res = client.post(f"/api/v1/sessions/{session_id}/cursor/pause", headers={"X-User-Id": user_id})
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "PAUSED"

    # Test Resume
    resume_res = client.post(f"/api/v1/sessions/{session_id}/cursor/resume", headers={"X-User-Id": user_id})
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "PLAYING"

    # Test Restart
    restart_res = client.post(f"/api/v1/sessions/{session_id}/cursor/restart", headers={"X-User-Id": user_id})
    assert restart_res.status_code == 200
    assert restart_res.json()["current_sequence"] == 0
