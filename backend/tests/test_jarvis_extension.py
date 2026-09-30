import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.jarvis.provider import GeminiAIProvider


@pytest.fixture
def client():
    return TestClient(app)


def test_jarvis_chat_endpoint(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Jarvis User"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    res = client.post(
        "/api/v1/jarvis/chat",
        json={"session_id": session_id, "user_id": user_id, "message": "What is a NameNode?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["session_id"] == session_id
    assert "intent" in data
    assert "text" in data


def test_jarvis_start_simulation_1gb_128mb(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Sim User"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    res = client.post(
        "/api/v1/jarvis/chat",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "Jarvis, create a 1 GB HDFS file using 128 MB blocks and replication factor 3."
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] in ["START_SIMULATION", "WRITE_FILE"]
    assert "8 blocks" in data["text"] or "8" in data["text"]
    assert data["visual_actions"] is not None


def test_jarvis_contextual_why_8_blocks(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Context User"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # First write 1 GB file
    client.post(
        "/api/v1/jarvis/chat",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "Create a 1 GB file with 128 MB blocks."
        }
    )

    # Ask contextual question
    res = client.post(
        "/api/v1/jarvis/chat",
        json={
            "session_id": session_id,
            "user_id": user_id,
            "message": "Why are there 8 blocks?"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "8" in data["text"]
    assert len(data["text"]) > 0


def test_jarvis_stop_and_resume(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Lifecycle User"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # STOP
    stop_res = client.post(
        "/api/v1/jarvis/chat",
        json={"session_id": session_id, "user_id": user_id, "message": "Jarvis, stop"}
    )
    assert stop_res.status_code == 200
    assert stop_res.json()["should_pause"] is True

    # RESUME
    resume_res = client.post(
        "/api/v1/jarvis/chat",
        json={"session_id": session_id, "user_id": user_id, "message": "continue"}
    )
    assert resume_res.status_code == 200
    assert resume_res.json()["should_resume"] is True


def test_jarvis_datanode_failure_and_recovery(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Failure User"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # Fail DN 3
    fail_res = client.post(
        "/api/v1/jarvis/chat",
        json={"session_id": session_id, "user_id": user_id, "message": "Kill DataNode 3"}
    )
    assert fail_res.status_code == 200
    assert fail_res.json()["intent"] in ["FAILURE_INJECTION", "KILL_NODE"]

    # Recover DN 3
    rec_res = client.post(
        "/api/v1/jarvis/chat",
        json={"session_id": session_id, "user_id": user_id, "message": "Recover DataNode 3"}
    )
    assert rec_res.status_code == 200
    assert rec_res.json()["intent"] in ["FAILURE_INJECTION", "RECOVER_NODE"]


def test_jarvis_quiz_and_misconception(client):
    user_res = client.post("/api/v1/users", json={"display_name": "Quiz User"})
    user_id = user_res.json()["user"]["user_id"]
    session_res = client.post("/api/v1/sessions", json={"user_id": user_id})
    session_id = session_res.json()["session"]["session_id"]

    # Quiz
    q_res = client.post(
        "/api/v1/jarvis/chat",
        json={"session_id": session_id, "user_id": user_id, "message": "Quiz me on HDFS"}
    )
    assert q_res.status_code == 200
    assert "QUIZ" in q_res.json()["text"] or q_res.json()["intent"] == "QUIZ"

    # Misconception
    mc_res = client.post(
        "/api/v1/jarvis/chat",
        json={"session_id": session_id, "user_id": user_id, "message": "The NameNode stores the actual file."}
    )
    assert mc_res.status_code == 200
    assert "MISCONCEPTION" in mc_res.json()["text"] or "metadata" in mc_res.json()["text"].lower()


def test_jarvis_rag_query_endpoint(client):
    res = client.post(
        "/api/v1/jarvis/rag/query",
        json={"query": "HDFS block size metadata", "top_k": 2}
    )
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert isinstance(data["results"], list)


def test_gemini_provider_fallback():
    provider = GeminiAIProvider(api_key="INVALID_TEST_KEY")
    res = provider.parse_user_message("What is HDFS?")
    assert isinstance(res, dict)
