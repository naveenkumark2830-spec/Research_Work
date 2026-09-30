from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_session():
    user_resp = client.post("/api/v1/users", json={"display_name": "File Test User"})
    user_id = user_resp.json()["user"]["user_id"]

    response = client.post(
        "/api/v1/sessions",
        json={"user_id": user_id},
    )

    assert response.status_code in (200, 201)

    data = response.json()

    session_id = (
        data.get("session_id")
        or data.get("id")
        or data.get("session", {}).get("session_id")
        or data.get("session", {}).get("id")
    )

    assert session_id is not None
    return session_id, user_id


def test_write_hdfs_file_api():
    session_id, user_id = create_session()

    response = client.post(
        "/api/v1/simulation/hdfs/file",
        json={
            "session_id": session_id,
            "path": "/teddy/api-test.txt",
            "size": 1,
            "unit": "MB",
            "user_id": user_id,
        },
    )

    assert response.status_code in (200, 201), response.text

    data = response.json()

    assert data is not None
