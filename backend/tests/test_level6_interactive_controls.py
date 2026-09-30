import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import init_db, SessionLocal
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.repositories.session_repository import SQLAlchemySessionRepository
from app.repositories.event_repository import SQLAlchemyEventRepository
from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.simulation.hdfs.engine import HDFSSimulationEngine
from app.simulation.hdfs.cluster import HDFSClusterConfig
from app.simulation.common.enums import DataNodeStatus, BlockState
from app.simulation.common.exceptions import InvalidClusterConfigurationError, InvalidSimulationStateError


@pytest.fixture
def client():
    init_db()
    with TestClient(app) as c:
        yield c


def test_1_configuration_validation_bounds():
    with pytest.raises(InvalidClusterConfigurationError):
        HDFSClusterConfig(file_size_mb=0)

    with pytest.raises(InvalidClusterConfigurationError):
        HDFSClusterConfig(block_size_mb=0)

    with pytest.raises(InvalidClusterConfigurationError):
        HDFSClusterConfig(replication_factor=0)

    with pytest.raises(InvalidClusterConfigurationError):
        HDFSClusterConfig(data_node_count=0)

    with pytest.raises(InvalidClusterConfigurationError):
        HDFSClusterConfig(reducer_count=0)

    with pytest.raises(InvalidClusterConfigurationError):
        HDFSClusterConfig(simulation_speed=0.0)


def test_2_file_block_calculation():
    cfg = HDFSClusterConfig(file_size_mb=500, block_size_mb=128, replication_factor=3, data_node_count=5)
    engine = HDFSSimulationEngine(config=cfg)
    file_obj, blocks = engine.write_file("test.csv", 524288000)

    assert len(blocks) == 4
    assert blocks[0].size_bytes == 134217728
    assert blocks[1].size_bytes == 134217728
    assert blocks[2].size_bytes == 134217728
    assert blocks[3].size_bytes == 121634816
    assert sum(b.size_bytes for b in blocks) == 524288000


def test_3_replication_factor_validation(client):
    user_res = client.post("/api/v1/users", json={"display_name": "RF Tester"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # Try setting RF=6 on 5 DataNodes -> Should fail with 400 Bad Request
    config_res = client.put(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/config",
        json={
            "user_id": user_id,
            "config": {
                "file_size_mb": 500,
                "block_size_mb": 128,
                "replication_factor": 6,
                "data_node_count": 5,
                "reducer_count": 5,
                "simulation_speed": 1.0
            }
        },
        headers={"X-User-Id": user_id}
    )
    assert config_res.status_code == 400
    assert "Replication factor 6 cannot exceed 5 available DataNodes." in config_res.json()["detail"]


def test_4_datanode_count_configuration(client):
    user_res = client.post("/api/v1/users", json={"display_name": "DN Count Tester"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    config_res = client.put(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/config",
        json={
            "user_id": user_id,
            "config": {
                "file_size_mb": 500,
                "block_size_mb": 128,
                "replication_factor": 3,
                "data_node_count": 10,
                "reducer_count": 5,
                "simulation_speed": 1.0
            }
        },
        headers={"X-User-Id": user_id}
    )
    assert config_res.status_code == 200

    cluster_res = client.get(f"/api/v1/simulation/hdfs/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert len(cluster_res.json()["datanodes"]) == 10


def test_5_add_datanode(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Add DN Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # Initialize 5 DN cluster
    client.post(
        "/api/v1/simulation/hdfs/cluster",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "config": {"file_size_mb": 500, "block_size_mb": 128, "replication_factor": 3, "data_node_count": 5}
        },
        headers={"X-User-Id": user_id}
    )

    add_res = client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes", headers={"X-User-Id": user_id})
    assert add_res.status_code == 201

    cluster_res = client.get(f"/api/v1/simulation/hdfs/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert len(cluster_res.json()["datanodes"]) == 6
    assert "datanode-6" in cluster_res.json()["datanodes"]


def test_6_remove_datanode(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Remove DN Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(
        "/api/v1/simulation/hdfs/cluster",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "config": {"file_size_mb": 500, "block_size_mb": 128, "replication_factor": 3, "data_node_count": 5}
        },
        headers={"X-User-Id": user_id}
    )
    client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "file.dat", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )

    del_res = client.delete(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-5", headers={"X-User-Id": user_id})
    assert del_res.status_code == 200

    cluster_res = client.get(f"/api/v1/simulation/hdfs/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert len(cluster_res.json()["datanodes"]) == 4
    assert "datanode-5" not in cluster_res.json()["datanodes"]


def test_7_kill_datanode(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Kill DN Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(
        "/api/v1/simulation/hdfs/cluster",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "config": {"file_size_mb": 500, "block_size_mb": 128, "replication_factor": 3, "data_node_count": 5}
        },
        headers={"X-User-Id": user_id}
    )

    kill_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/kill",
        headers={"X-User-Id": user_id}
    )
    assert kill_res.status_code == 200

    cluster_res = client.get(f"/api/v1/simulation/hdfs/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert cluster_res.json()["datanodes"]["datanode-1"]["status"] == "FAILED"


def test_8_recover_datanode(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Recover DN Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(
        "/api/v1/simulation/hdfs/cluster",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "config": {"file_size_mb": 500, "block_size_mb": 128, "replication_factor": 3, "data_node_count": 5}
        },
        headers={"X-User-Id": user_id}
    )

    client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/kill", headers={"X-User-Id": user_id})
    rec_res = client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/recover", headers={"X-User-Id": user_id})
    assert rec_res.status_code == 200

    cluster_res = client.get(f"/api/v1/simulation/hdfs/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert cluster_res.json()["datanodes"]["datanode-1"]["status"] == "LIVE"


def test_9_under_replication_after_failure_and_removal(client):
    user_res = client.post("/api/v1/users", json={"display_name": "UnderRep Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(
        "/api/v1/simulation/hdfs/cluster",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "config": {"file_size_mb": 500, "block_size_mb": 128, "replication_factor": 3, "data_node_count": 5}
        },
        headers={"X-User-Id": user_id}
    )
    client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "file.dat", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )

    client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/kill", headers={"X-User-Id": user_id})

    cluster_res = client.get(f"/api/v1/simulation/hdfs/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    under_rep = [
        b for b in cluster_res.json()["blocks"].values()
        if "datanode-1" in b["replica_nodes"] or len(b["replica_nodes"]) < 3
    ]
    assert len(under_rep) > 0


def test_10_configuration_persistence(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Config Persist"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.put(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/config",
        json={
            "user_id": user_id,
            "config": {
                "file_size_mb": 800,
                "block_size_mb": 256,
                "replication_factor": 3,
                "data_node_count": 5,
                "reducer_count": 8,
                "simulation_speed": 2.0
            }
        },
        headers={"X-User-Id": user_id}
    )

    state_res = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    cfg = state_res.json()["simulation"]["configuration"]
    assert cfg["file_size_mb"] == 800
    assert cfg["block_size_mb"] == 256
    assert cfg["reducer_count"] == 8
    assert cfg["simulation_speed"] == 2.0


def test_11_pause_simulation(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Pause Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})
    pause_res = client.post(f"/api/v1/sessions/{session_id}/pause", headers={"X-User-Id": user_id})
    assert pause_res.status_code == 200
    assert pause_res.json()["simulation"]["status"] == "PAUSED"


def test_12_resume_simulation(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Resume Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})
    client.post(f"/api/v1/sessions/{session_id}/pause", headers={"X-User-Id": user_id})
    resume_res = client.post(f"/api/v1/sessions/{session_id}/resume", headers={"X-User-Id": user_id})
    assert resume_res.status_code == 200
    assert resume_res.json()["simulation"]["status"] == "RUNNING"


def test_13_restart_simulation(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Restart Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "file.dat", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )

    restart_res = client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/restart", headers={"X-User-Id": user_id})
    assert restart_res.status_code == 200

    cluster_res = client.get(f"/api/v1/simulation/hdfs/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert len(cluster_res.json()["files"]) == 0
    assert len(cluster_res.json()["blocks"]) == 0


def test_14_simulation_speed_configuration(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Speed Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    speed_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/speed",
        json={"user_id": user_id, "speed": 4.0},
        headers={"X-User-Id": user_id}
    )
    assert speed_res.status_code == 200
    assert speed_res.json()["simulation"]["configuration"]["simulation_speed"] == 4.0


def test_15_reducer_count_configuration(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Reducers Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.put(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/config",
        json={
            "user_id": user_id,
            "config": {
                "file_size_mb": 500,
                "block_size_mb": 128,
                "replication_factor": 3,
                "data_node_count": 5,
                "reducer_count": 12,
                "simulation_speed": 1.0
            }
        },
        headers={"X-User-Id": user_id}
    )

    state_res = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert state_res.json()["simulation"]["configuration"]["reducer_count"] == 12


def test_16_event_generation(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Events Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes", headers={"X-User-Id": user_id})

    events_res = client.get(f"/api/v1/sessions/{session_id}/events", headers={"X-User-Id": user_id})
    assert events_res.status_code == 200
    events = events_res.json()
    types = [e["event_type"] for e in events]
    assert "DATANODE_ADDED" in types or "SIMULATION_UPDATED" in types


def test_17_event_sequence_monotonicity(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Seq Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes", headers={"X-User-Id": user_id})
    client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes", headers={"X-User-Id": user_id})

    events = client.get(f"/api/v1/sessions/{session_id}/events", headers={"X-User-Id": user_id}).json()
    seqs = [e["sequence_number"] for e in events]
    assert seqs == sorted(seqs)
    assert len(seqs) == len(set(seqs))


def test_18_session_isolation(client):
    # Create Session A and Session B
    userA = client.post("/api/v1/users", json={"display_name": "User A"}).json()["user"]["user_id"]
    userB = client.post("/api/v1/users", json={"display_name": "User B"}).json()["user"]["user_id"]

    sesA = client.post("/api/v1/sessions", json={"user_id": userA}).json()["session"]["session_id"]
    sesB = client.post("/api/v1/sessions", json={"user_id": userB}).json()["session"]["session_id"]

    # Configure Session A to 8 DataNodes
    client.put(
        f"/api/v1/simulation/hdfs/sessions/{sesA}/config",
        json={
            "user_id": userA,
            "config": {
                "file_size_mb": 500,
                "block_size_mb": 128,
                "replication_factor": 3,
                "data_node_count": 8,
                "reducer_count": 5,
                "simulation_speed": 1.0
            }
        },
        headers={"X-User-Id": userA}
    )

    # Configure Session B to 10 DataNodes
    client.put(
        f"/api/v1/simulation/hdfs/sessions/{sesB}/config",
        json={
            "user_id": userB,
            "config": {
                "file_size_mb": 500,
                "block_size_mb": 128,
                "replication_factor": 3,
                "data_node_count": 10,
                "reducer_count": 5,
                "simulation_speed": 1.0
            }
        },
        headers={"X-User-Id": userB}
    )

    # Verify Session A remains 8 DataNodes and Session B remains 10 DataNodes
    stateA = client.get(f"/api/v1/simulation/hdfs/sessions/{sesA}/state", headers={"X-User-Id": userA}).json()
    stateB = client.get(f"/api/v1/simulation/hdfs/sessions/{sesB}/state", headers={"X-User-Id": userB}).json()

    assert len(stateA["datanodes"]) == 8
    assert len(stateB["datanodes"]) == 10


def test_19_invalid_datanode_action_conflict(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Conflict Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(
        "/api/v1/simulation/hdfs/cluster",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "config": {"file_size_mb": 500, "block_size_mb": 128, "replication_factor": 3, "data_node_count": 5}
        },
        headers={"X-User-Id": user_id}
    )

    # Recovering an already live DataNode -> 409 Conflict
    rec_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/recover",
        headers={"X-User-Id": user_id}
    )
    assert rec_res.status_code == 409

    # Kill DataNode-1 once
    client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/kill",
        headers={"X-User-Id": user_id}
    )

    # Killing an already failed DataNode -> 409 Conflict
    kill_again_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/kill",
        headers={"X-User-Id": user_id}
    )
    assert kill_again_res.status_code == 409


def test_20_modify_config_while_running_conflict(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Running Config Tester"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # Start simulation
    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    # Updating config while RUNNING -> 409 Conflict
    config_res = client.put(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/config",
        json={
            "user_id": user_id,
            "config": {
                "file_size_mb": 800,
                "block_size_mb": 128,
                "replication_factor": 3,
                "data_node_count": 5,
                "reducer_count": 5,
                "simulation_speed": 1.0
            }
        },
        headers={"X-User-Id": user_id}
    )
    assert config_res.status_code == 409


def test_21_frontend_api_contract_end_to_end(client):
    # Full Level 6 Lifecycle Acceptance Flow
    user_id = client.post("/api/v1/users", json={"display_name": "EndToEnd"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    # Apply initial config: 500MB, 128MB, RF=3, 5 DNs
    client.put(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/config",
        json={
            "user_id": user_id,
            "config": {
                "file_size_mb": 500,
                "block_size_mb": 128,
                "replication_factor": 3,
                "data_node_count": 5,
                "reducer_count": 5,
                "simulation_speed": 1.0
            }
        },
        headers={"X-User-Id": user_id}
    )

    # Start HDFS Write
    write_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "data.csv", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )
    assert write_res.status_code == 200

    # Add DataNode-6
    add_res = client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes", headers={"X-User-Id": user_id})
    assert add_res.status_code == 201

    # Kill DataNode-3
    kill_res = client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-3/kill", headers={"X-User-Id": user_id})
    assert kill_res.status_code == 200

    # Recover DataNode-3
    rec_res = client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-3/recover", headers={"X-User-Id": user_id})
    assert rec_res.status_code == 200

    # Restart
    restart_res = client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/restart", headers={"X-User-Id": user_id})
    assert restart_res.status_code == 200
