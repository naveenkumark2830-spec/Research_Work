def test_hdfs_api_full_scenario(client):
    # 1. Setup user and session
    user_res = client.post("/api/v1/users", json={"display_name": "API User"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # 2. Write file
    write_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "sales_data.csv", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )
    assert write_res.status_code == 200
    state = write_res.json()
    assert state["simulation"]["system"] == "HDFS"

    # 3. Read file
    read_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/read",
        json={"user_id": user_id, "path": "sales_data.csv"},
        headers={"X-User-Id": user_id}
    )
    assert read_res.status_code == 200
    assert read_res.json()["total_bytes"] == 524288000
    assert len(read_res.json()["read_plan"]) == 4

    # 4. Fail datanode-1
    fail_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/fail",
        headers={"X-User-Id": user_id}
    )
    assert fail_res.status_code == 200

    # 5. Recover under-replicated blocks
    rec_res = client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/recover",
        headers={"X-User-Id": user_id}
    )
    assert rec_res.status_code == 200

    # 6. Fetch cluster state
    cluster_res = client.get(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/state",
        headers={"X-User-Id": user_id}
    )
    assert cluster_res.status_code == 200
    cluster_state = cluster_res.json()
    assert cluster_state["datanodes"]["datanode-1"]["status"] == "FAILED"
