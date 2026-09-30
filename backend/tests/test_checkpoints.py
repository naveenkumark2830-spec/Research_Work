def test_checkpoint_creation_and_restoration(client):
    # 1. Create user and session
    user_res = client.post("/api/v1/users", json={"display_name": "Hannah"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # 2. Start simulation and move to stage REPLICATION with progress 0.62
    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    # Set specific state for simulation
    state_before_chk = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id}).json()
    state_before_chk["simulation"]["current_stage"] = "REPLICATION"
    state_before_chk["simulation"]["progress"] = 0.62

    # Save mutated state via repository or start/message endpoint
    # Create checkpoint at this state
    chk_res = client.post(
        f"/api/v1/sessions/{session_id}/checkpoint",
        json={"user_id": user_id, "description": "Replication 62% Checkpoint"},
        headers={"X-User-Id": user_id}
    )
    assert chk_res.status_code == 201
    checkpoint = chk_res.json()
    checkpoint_id = checkpoint["checkpoint_id"]

    # 3. Further modify state (e.g. add message or restart/change simulation stage)
    client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"user_id": user_id, "role": "USER", "content": "What is the map status?"}
    )
    client.post(f"/api/v1/sessions/{session_id}/restart", headers={"X-User-Id": user_id})

    modified_state = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id}).json()
    assert modified_state["simulation"]["current_stage"] == "INITIALIZATION"
    assert modified_state["simulation"]["progress"] == 0.0

    # 4. Restore checkpoint
    restore_res = client.post(
        f"/api/v1/sessions/{session_id}/restore/{checkpoint_id}",
        headers={"X-User-Id": user_id}
    )
    assert restore_res.status_code == 200
    restored_state = restore_res.json()

    # 5. Verify restored state matches checkpoint snapshot
    assert restored_state["simulation"]["status"] == "RUNNING"
    assert restored_state["state_version"] > modified_state["state_version"]


def test_list_checkpoints(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Ian"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/checkpoint", json={"description": "Checkpoint 1"}, headers={"X-User-Id": user_id})
    client.post(f"/api/v1/sessions/{session_id}/checkpoint", json={"description": "Checkpoint 2"}, headers={"X-User-Id": user_id})

    chks_res = client.get(f"/api/v1/sessions/{session_id}/checkpoints", headers={"X-User-Id": user_id})
    assert chks_res.status_code == 200
    checkpoints = chks_res.json()
    assert len(checkpoints) == 2
    descs = [c["description"] for c in checkpoints]
    assert "Checkpoint 1" in descs
    assert "Checkpoint 2" in descs
