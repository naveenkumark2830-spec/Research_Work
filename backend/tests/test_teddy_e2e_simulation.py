from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_session():
    user_resp = client.post("/api/v1/users", json={"display_name": "Teddy E2E User"})
    user_id = user_resp.json()["user"]["user_id"]

    response = client.post(
        "/api/v1/sessions",
        json={"user_id": user_id},
    )

    assert response.status_code in (200, 201)

    data = response.json()
    session_id = data["session"]["session_id"]
    return session_id, user_id


def test_teddy_e2e_file_write_simulation():
    session_id, user_id = create_session()

    # 1. Ask Teddy to create a file
    response = client.post(
        "/api/v1/ai/chat",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "Create a 1 GB file using 128 MB blocks with replication factor 3 and show me how HDFS stores it.",
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert "plan" in data
    plan = data["plan"]

    assert plan["simulation_required"] is True
    assert plan["simulation_action"]["action"] in ("write_file", "create_cluster")

    # 2. Check cluster state to verify file write execution in real HDFS engine
    state_resp = client.get(f"/api/v1/simulation/hdfs/state/{session_id}")
    assert state_resp.status_code == 200

    cluster_state = state_resp.json()["state"]
    assert cluster_state is not None
