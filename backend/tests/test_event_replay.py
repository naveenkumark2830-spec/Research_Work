import pytest
from app.simulation.hdfs.cluster import HDFSClusterConfig
from app.simulation.hdfs.engine import HDFSSimulationEngine


def test_deterministic_event_replay(client):
    # 1. Setup user & session
    user_res = client.post("/api/v1/users", json={"display_name": "Replay User"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # 2. Perform HDFS cluster write
    client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "data.csv", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )

    live_state = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id}).json()

    # 3. Replay events into isolated state
    replay_res = client.post(
        f"/api/v1/sessions/{session_id}/replay",
        json={"user_id": user_id},
        headers={"X-User-Id": user_id}
    )
    assert replay_res.status_code == 200
    replayed = replay_res.json()["replayed_state"]

    # 4. Verify replayed state matches original live state
    assert replayed["session"]["session_id"] == live_state["session"]["session_id"]
    assert replayed["simulation"]["system"] == live_state["simulation"]["system"]


def test_failure_and_recovery_replay(client):
    # Failure & Recovery Replay Test
    user_res = client.post("/api/v1/users", json={"display_name": "Failure User"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "fail.csv", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )
    client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-1/fail", headers={"X-User-Id": user_id})
    client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/recover", headers={"X-User-Id": user_id})

    live_state = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id}).json()

    replay_res = client.post(
        f"/api/v1/sessions/{session_id}/replay",
        json={"user_id": user_id},
        headers={"X-User-Id": user_id}
    )
    assert replay_res.status_code == 200
    replayed = replay_res.json()["replayed_state"]

    assert replayed["simulation"]["status"] == live_state["simulation"]["status"]


def test_critical_requirement_45_pause_question_resume(client):
    # Requirement 45: Pause at event sequence, query state, resume without restarting/duplicating
    user_res = client.post("/api/v1/users", json={"display_name": "Req45 User"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    # Pause playback at current sequence
    pause_res = client.post(f"/api/v1/sessions/{session_id}/cursor/pause", headers={"X-User-Id": user_id})
    assert pause_res.status_code == 200
    cursor_before = pause_res.json()
    seq_paused = cursor_before["current_sequence"]

    # User asks a question (adds conversation message)
    msg_res = client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"user_id": user_id, "role": "USER", "content": "Why are there 3 replicas?"}
    )
    assert msg_res.status_code == 200

    # User says "continue" (resumes playback)
    resume_res = client.post(f"/api/v1/sessions/{session_id}/cursor/resume", headers={"X-User-Id": user_id})
    assert resume_res.status_code == 200
    cursor_after = resume_res.json()

    # Cursor continues cleanly without resetting or corrupting timeline
    assert cursor_after["status"] == "PLAYING"
    assert cursor_after["total_events"] > seq_paused
