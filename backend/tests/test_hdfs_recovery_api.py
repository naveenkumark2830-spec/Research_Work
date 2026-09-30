from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_session():
    user_resp = client.post("/api/v1/users", json={"display_name": "Recovery Test User"})
    user_id = user_resp.json()["user"]["user_id"]

    response = client.post(
        "/api/v1/sessions",
        json={"user_id": user_id},
    )

    assert response.status_code in (200, 201)
    data = response.json()
    session_id = data["session"]["session_id"]

    # Initialize cluster
    client.post(
        "/api/v1/simulation/hdfs/cluster",
        headers={"X-User-Id": user_id},
        json={"session_id": session_id},
    )

    # Query cluster state for node_id
    state_resp = client.get(f"/api/v1/simulation/hdfs/state/{session_id}")
    nodes = state_resp.json()["state"]["datanodes"]
    node_id = list(nodes.keys())[0]

    return session_id, user_id, node_id


def test_datanode_recovery_api():
    session_id, user_id, node_id = create_session()

    # Fail DataNode first so it can be recovered
    fail_resp = client.post(
        "/api/v1/simulation/hdfs/failure",
        json={
            "session_id": session_id,
            "node_id": node_id,
            "user_id": user_id,
        },
    )
    assert fail_resp.status_code in (200, 201)

    response = client.post(
        "/api/v1/simulation/hdfs/recovery",
        json={
            "session_id": session_id,
            "node_id": node_id,
            "user_id": user_id,
        },
    )

    assert response.status_code in (200, 201), response.text
