def test_initial_simulation_state_is_idle(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Grace"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    state_res = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert state_res.json()["simulation"]["status"] == "IDLE"


def test_start_simulation_idle_to_running(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Grace"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    start_res = client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})
    assert start_res.status_code == 200
    state = start_res.json()
    assert state["simulation"]["status"] == "RUNNING"
    assert state["visualization"]["status"] == "PLAYING"
    assert state["state_version"] == 2


def test_running_to_paused(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Grace"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    pause_res = client.post(f"/api/v1/sessions/{session_id}/pause", headers={"X-User-Id": user_id})
    assert pause_res.status_code == 200
    state = pause_res.json()
    assert state["simulation"]["status"] == "PAUSED"
    assert state["visualization"]["status"] == "PAUSED"
    assert state["voice"]["status"] == "INTERRUPTED"
    assert state["voice"]["interruption_requested"] is True


def test_paused_to_running_resume(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Grace"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})
    client.post(f"/api/v1/sessions/{session_id}/pause", headers={"X-User-Id": user_id})

    resume_res = client.post(f"/api/v1/sessions/{session_id}/resume", headers={"X-User-Id": user_id})
    assert resume_res.status_code == 200
    state = resume_res.json()
    assert state["simulation"]["status"] == "RUNNING"
    assert state["visualization"]["status"] == "PLAYING"


def test_running_to_restart(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Grace"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    restart_res = client.post(f"/api/v1/sessions/{session_id}/restart", headers={"X-User-Id": user_id})
    assert restart_res.status_code == 200
    state = restart_res.json()
    assert state["simulation"]["status"] == "RUNNING"
    assert state["simulation"]["current_stage"] == "INITIALIZATION"
    assert state["simulation"]["progress"] == 0.0


def test_invalid_transitions_rejected(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Grace"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # IDLE -> RESUME should fail
    resume_res = client.post(f"/api/v1/sessions/{session_id}/resume", headers={"X-User-Id": user_id})
    assert resume_res.status_code == 400
    assert "Cannot execute 'RESUME'" in resume_res.json()["detail"]

    # Start simulation -> RUNNING
    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    # RUNNING -> START should fail
    start_res = client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})
    assert start_res.status_code == 400
    assert "Cannot execute 'START'" in start_res.json()["detail"]
