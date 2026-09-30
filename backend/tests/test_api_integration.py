from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"


def test_create_session():
    user_response = client.post(
        "/api/v1/users",
        json={"display_name": "Test API User"},
    )
    assert user_response.status_code in (200, 201)
    user_id = user_response.json()["user"]["user_id"]

    response = client.post(
        "/api/v1/sessions",
        json={
            "user_id": user_id,
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert "session" in data
    assert data["session"]["user_id"] == user_id


def test_create_hdfs_cluster():
    user_response = client.post(
        "/api/v1/users",
        json={"display_name": "Test API User"},
    )
    assert user_response.status_code in (200, 201)
    user_id = user_response.json()["user"]["user_id"]

    session_response = client.post(
        "/api/v1/sessions",
        json={
            "user_id": user_id,
        },
    )

    assert session_response.status_code in (200, 201)

    session_data = session_response.json()
    session_id = session_data["session"]["session_id"]

    response = client.post(
        "/api/v1/simulation/hdfs/cluster",
        headers={
            "X-User-Id": user_id,
        },
        json={
            "session_id": session_id,
            "file_size_mb": 1024,
            "block_size_mb": 128,
            "replication_factor": 3,
            "data_node_count": 5,
        },
    )

    assert response.status_code in (200, 201)

    data = response.json()

    assert data is not None
