from app.simulation.hdfs.cluster import HDFSClusterConfig
from app.simulation.hdfs.engine import HDFSSimulationEngine


def test_simulation_determinism():
    # TEST 21 & TEST 20: Same configuration produces 100% identical outputs
    cfg = HDFSClusterConfig(file_size_bytes=524288000, block_size_bytes=134217728, replication_factor=3, data_node_count=5)

    # Run 1
    engine1 = HDFSSimulationEngine(config=cfg)
    file1, blocks1 = engine1.write_file("customers.csv", 524288000)
    engine1.fail_datanode("datanode-1")
    engine1.recover_under_replicated_blocks()
    events1 = engine1.get_events()
    state1 = engine1.get_cluster_state().model_dump(mode="json")

    # Run 2
    engine2 = HDFSSimulationEngine(config=cfg)
    file2, blocks2 = engine2.write_file("customers.csv", 524288000)
    engine2.fail_datanode("datanode-1")
    engine2.recover_under_replicated_blocks()
    events2 = engine2.get_events()
    state2 = engine2.get_cluster_state().model_dump(mode="json")

    # Assert 100% identical execution outcomes
    assert file1.block_ids == file2.block_ids
    assert [b.size_bytes for b in blocks1] == [b.size_bytes for b in blocks2]
    assert [b.replica_nodes for b in blocks1] == [b.replica_nodes for b in blocks2]
    assert len(events1) == len(events2)
    assert [e["event_type"] for e in events1] == [e["event_type"] for e in events2]
    assert state1 == state2


def test_session_isolation_independent_clusters(client):
    # TEST 22: Multiple sessions have independent HDFS clusters
    user_res = client.post("/api/v1/users", json={"display_name": "Session Isolation User"})
    user_id = user_res.json()["user"]["user_id"]

    s1 = client.post("/api/v1/sessions", json={"user_id": user_id}).json()
    s2 = client.post("/api/v1/sessions", json={"user_id": user_id}).json()

    s1_id = s1["session"]["session_id"]
    s2_id = s2["session"]["session_id"]

    # Write file to Session 1 HDFS cluster
    client.post(
        f"/api/v1/simulation/hdfs/sessions/{s1_id}/write",
        json={"user_id": user_id, "path": "file1.csv", "size_bytes": 1000000}
    )

    # Verify Session 1 has file1.csv while Session 2 HDFS cluster is empty
    state1 = client.get(f"/api/v1/simulation/hdfs/sessions/{s1_id}/state", headers={"X-User-Id": user_id}).json()
    state2 = client.get(f"/api/v1/simulation/hdfs/sessions/{s2_id}/state", headers={"X-User-Id": user_id}).json()

    assert "file1.csv" in state1["files"]
    assert "file1.csv" not in state2["files"]
