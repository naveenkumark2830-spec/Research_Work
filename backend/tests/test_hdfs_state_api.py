from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_session():
    user_resp = client.post("/api/v1/users", json={"display_name": "State Test User"})
    user_id = user_resp.json()["user"]["user_id"]

    response = client.post(
        "/api/v1/sessions",
        json={"user_id": user_id},
    )

    assert response.status_code in (200, 201)

    data = response.json()

    return (
        data.get("session_id")
        or data.get("id")
        or data.get("session", {}).get("session_id")
        or data.get("session", {}).get("id")
    )


def test_get_hdfs_state():
    session_id = create_session()

    response = client.get(
        f"/api/v1/simulation/hdfs/state/{session_id}"
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data is not None
