def test_multiple_sessions_isolated(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Jack"})
    user_id = user_res.json()["user"]["user_id"]

    session1 = client.post("/api/v1/sessions", json={"user_id": user_id}).json()
    session2 = client.post("/api/v1/sessions", json={"user_id": user_id}).json()

    s1_id = session1["session"]["session_id"]
    s2_id = session2["session"]["session_id"]

    # Start simulation on session 1 only
    client.post(f"/api/v1/sessions/{s1_id}/start", headers={"X-User-Id": user_id})

    # Verify session 1 is RUNNING while session 2 remains IDLE
    state1 = client.get(f"/api/v1/sessions/{s1_id}/state", headers={"X-User-Id": user_id}).json()
    state2 = client.get(f"/api/v1/sessions/{s2_id}/state", headers={"X-User-Id": user_id}).json()

    assert state1["simulation"]["status"] == "RUNNING"
    assert state2["simulation"]["status"] == "IDLE"


def test_user_cannot_access_another_user_session(client):
    user1_res = client.post("/api/v1/users", json={"display_name": "User 1"})
    user1_id = user1_res.json()["user"]["user_id"]

    user2_res = client.post("/api/v1/users", json={"display_name": "User 2"})
    user2_id = user2_res.json()["user"]["user_id"]

    # User 1 creates session
    session1 = client.post("/api/v1/sessions", json={"user_id": user1_id}).json()
    s1_id = session1["session"]["session_id"]

    # User 2 attempts to fetch state of session 1 -> should fail with 403 Forbidden
    forbidden_res = client.get(f"/api/v1/sessions/{s1_id}/state", headers={"X-User-Id": user2_id})
    assert forbidden_res.status_code == 403
    assert "does not have authorization" in forbidden_res.json()["detail"]
