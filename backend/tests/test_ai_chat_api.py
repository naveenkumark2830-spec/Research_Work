from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def create_session():
    user_resp = client.post("/api/v1/users", json={"display_name": "AI Chat User"})
    user_id = user_resp.json()["user"]["user_id"]

    response = client.post(
        "/api/v1/sessions",
        json={"user_id": user_id},
    )

    assert response.status_code in (200, 201)

    data = response.json()

    session_id = data["session"]["session_id"]
    return session_id, user_id


def test_teddy_chat_api():
    session_id, user_id = create_session()

    response = client.post(
        "/api/v1/ai/chat",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "What does the NameNode do in HDFS?",
        },
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert "plan" in data or "answer" in data
    if "plan" in data:
        assert "answer" in data["plan"]
