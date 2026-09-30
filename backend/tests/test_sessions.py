def test_session_creation(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Charlie"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id, "current_topic": "HDFS Replication"})
    assert session_res.status_code == 201
    state = session_res.json()
    assert state["session"]["user_id"] == user_id
    assert state["session"]["current_topic"] == "HDFS Replication"
    assert state["simulation"]["status"] == "IDLE"
    assert state["state_version"] == 1


def test_session_belongs_to_correct_user(client):
    user_res = client.post("/api/v1/users", json={"display_name": "David"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    state_res = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id})
    assert state_res.status_code == 200
    assert state_res.json()["user"]["user_id"] == user_id


def test_conversation_message_persisted(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Eve"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    msg_res = client.post(
        f"/api/v1/sessions/{session_id}/messages",
        json={"user_id": user_id, "role": "USER", "content": "How does HDFS handle NameNode failures?"}
    )
    assert msg_res.status_code == 200
    updated_state = msg_res.json()
    assert updated_state["conversation"]["conversation_turn_count"] == 1
    assert updated_state["conversation"]["last_user_message"] == "How does HDFS handle NameNode failures?"
    assert len(updated_state["conversation"]["recent_messages"]) == 1
    assert updated_state["state_version"] == 2


def test_event_generated_for_state_change(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Frank"})
    user_id = user_res.json()["user"]["user_id"]

    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    events_res = client.get(f"/api/v1/sessions/{session_id}/events", headers={"X-User-Id": user_id})
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) >= 2  # SESSION_CREATED, SIMULATION_STARTED
    event_types = [e["event_type"] for e in events]
    assert "SESSION_CREATED" in event_types
    assert "SIMULATION_STARTED" in event_types
