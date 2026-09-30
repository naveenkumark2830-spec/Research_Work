def test_event_cursor_pause_resume_restart(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Cursor User"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # Check initial cursor
    cursor_res = client.get(f"/api/v1/sessions/{session_id}/cursor", headers={"X-User-Id": user_id})
    assert cursor_res.status_code == 200
    assert cursor_res.json()["session_id"] == session_id

    # Pause cursor
    pause_res = client.post(f"/api/v1/sessions/{session_id}/cursor/pause", headers={"X-User-Id": user_id})
    assert pause_res.status_code == 200
    assert pause_res.json()["status"] == "PAUSED"

    # Resume cursor
    resume_res = client.post(f"/api/v1/sessions/{session_id}/cursor/resume", headers={"X-User-Id": user_id})
    assert resume_res.status_code == 200
    assert resume_res.json()["status"] == "PLAYING"

    # Restart cursor
    restart_res = client.post(f"/api/v1/sessions/{session_id}/cursor/restart", headers={"X-User-Id": user_id})
    assert restart_res.status_code == 200
    assert restart_res.json()["current_sequence"] == 0


def test_timeline_endpoint(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Timeline User"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(
        f"/api/v1/simulation/hdfs/sessions/{session_id}/write",
        json={"user_id": user_id, "path": "tl.csv", "size_bytes": 524288000},
        headers={"X-User-Id": user_id}
    )

    tl_res = client.get(f"/api/v1/sessions/{session_id}/timeline", headers={"X-User-Id": user_id})
    assert tl_res.status_code == 200
    tl = tl_res.json()
    assert tl["session_id"] == session_id
    assert tl["total_events"] > 0
    assert len(tl["events"]) == tl["total_events"]
    assert tl["events"][0]["sequence_number"] == 1
