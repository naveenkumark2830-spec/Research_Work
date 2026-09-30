import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ai.intent import IntentType
from app.ai.action import ActionType, Action, IntentResult
from app.ai.context import AIContext
from app.ai.provider import MockAIProvider
from app.ai.validator import ActionValidator
from app.ai.exceptions import InvalidAIActionError


@pytest.fixture
def client():
    return TestClient(app)


def test_1_intent_model_validation():
    result = IntentResult(
        intent=IntentType.MODIFY_SIMULATION,
        confidence=0.98,
        action=Action(type=ActionType.UPDATE_CONFIG, parameters={"block_size_mb": 256}),
        response="Changing block size to 256 MB."
    )
    assert result.intent == IntentType.MODIFY_SIMULATION
    assert result.action.type == ActionType.UPDATE_CONFIG
    assert result.action.parameters["block_size_mb"] == 256


def test_2_structured_action_validation():
    action = Action(type=ActionType.SET_SPEED, parameters={"speed": 2.0})
    ActionValidator.validate_action(action, {})
    assert action.parameters["speed"] == 2.0

    # Invalid speed should raise InvalidAIActionError
    invalid_speed = Action(type=ActionType.SET_SPEED, parameters={"speed": 50.0})
    with pytest.raises(InvalidAIActionError):
        ActionValidator.validate_action(invalid_speed, {})


def test_3_mock_ai_provider():
    provider = MockAIProvider()
    ctx = AIContext(user_message="Set block size to 256 MB.")
    res = provider.generate_structured_response(ctx)
    assert res.intent == IntentType.MODIFY_SIMULATION
    assert res.action.type == ActionType.UPDATE_CONFIG
    assert res.action.parameters["block_size_mb"] == 256


def test_4_explain_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Explain User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "What is a NameNode?"},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "EXPLAIN"
    assert "NameNode" in data["response"]


def test_5_modify_simulation_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Modify User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Set the block size to 256 MB."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "MODIFY_SIMULATION"
    assert data["action_executed"] is True
    assert data["simulation_state"]["configuration"]["block_size_mb"] == 256


def test_6_start_simulation_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Start User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Start the HDFS simulation."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "START_SIMULATION"
    assert data["action_executed"] is True


def test_7_pause_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Pause User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Pause."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "PAUSE"
    assert data["action_executed"] is True


def test_8_stop_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Stop User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Jarvis, stop."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "STOP"
    assert data["action_executed"] is True


def test_9_resume_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Resume User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    client.post(f"/api/v1/sessions/{session_id}/start", headers={"X-User-Id": user_id})
    client.post(f"/api/v1/sessions/{session_id}/pause", headers={"X-User-Id": user_id})

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Continue."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "RESUME"
    assert data["action_executed"] is True


def test_10_restart_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Restart User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Restart the simulation."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "RESTART"
    assert data["action_executed"] is True


def test_11_set_speed_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Speed User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Set speed to 2x."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["action_executed"] is True
    assert data["simulation_state"]["configuration"]["simulation_speed"] == 2.0


def test_12_add_datanode_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Add DN User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Add a DataNode."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "SCALE"
    assert data["action_executed"] is True
    assert len(data["simulation_state"]["datanodes"]) == 6


def test_13_remove_datanode_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Remove DN User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Remove DataNode 5."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["action_executed"] is True
    assert "datanode-5" not in data["simulation_state"]["datanodes"]


def test_14_kill_datanode_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Kill DN User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Kill DataNode 3."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "FAILURE_INJECTION"
    assert data["action_executed"] is True
    assert data["simulation_state"]["datanodes"]["datanode-3"]["status"] == "FAILED"


def test_15_recover_datanode_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Recover DN User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes/datanode-3/kill", headers={"X-User-Id": user_id})

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Recover DataNode 3."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["action_executed"] is True
    assert data["simulation_state"]["datanodes"]["datanode-3"]["status"] == "LIVE"


def test_16_show_component_intent(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Show Comp User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={
            "user_id": user_id,
            "message": "Explain this.",
            "visualization_context": {"selected_component": "datanode-3", "selected_component_type": "DATANODE"}
        },
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert "datanode-3" in data["response"]


def test_17_contextual_followup(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Followup User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Kill DataNode 3."},
        headers={"X-User-Id": user_id}
    )

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "What just happened?"},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert "event" in data["response"].lower() or "datanode" in data["response"].lower()


def test_18_ambiguous_request(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Ambiguous User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Make it bigger."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["action_executed"] is False
    assert data["clarification_question"] is not None


def test_19_invalid_action(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Invalid Action User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    invalid_act = Action(type=ActionType.SET_SPEED, parameters={"speed": 99.0})
    with pytest.raises(InvalidAIActionError):
        ActionValidator.validate_action(invalid_act, {})


def test_20_backend_validation_failure(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Validation Fail User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    # Try setting RF 10 when only 5 DataNodes exist -> backend rejection
    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Set replication to 10."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["action_executed"] is False
    assert "cannot exceed" in data["response"] or "5" in data["response"]


def test_21_session_isolation(client):
    userA = client.post("/api/v1/users", json={"display_name": "User A"}).json()["user"]["user_id"]
    userB = client.post("/api/v1/users", json={"display_name": "User B"}).json()["user"]["user_id"]

    sesA = client.post("/api/v1/sessions", json={"user_id": userA}).json()["session"]["session_id"]
    sesB = client.post("/api/v1/sessions", json={"user_id": userB}).json()["session"]["session_id"]

    client.post(
        f"/api/v1/ai/sessions/{sesA}/message",
        json={"user_id": userA, "message": "Set block size to 256 MB."},
        headers={"X-User-Id": userA}
    )

    stateA = client.get(f"/api/v1/simulation/hdfs/sessions/{sesA}/state", headers={"X-User-Id": userA}).json()
    stateB = client.get(f"/api/v1/simulation/hdfs/sessions/{sesB}/state", headers={"X-User-Id": userB}).json()

    assert stateA["configuration"]["block_size_mb"] == 256
    assert stateB["configuration"]["block_size_mb"] == 128


def test_22_no_api_key_mock_mode(client):
    # Verify mock provider runs gracefully without external API key
    user_id = client.post("/api/v1/users", json={"display_name": "Offline User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Add a DataNode."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    assert res.json()["action_executed"] is True


def test_23_ai_cannot_execute_arbitrary_code():
    action = Action(type=ActionType.UPDATE_CONFIG, parameters={"eval": "import os; os.system('calc')"})
    with pytest.raises(InvalidAIActionError):
        ActionValidator.validate_action(action, {})


def test_24_event_generation_through_existing_event_engine(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Evt User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Kill DataNode 3."},
        headers={"X-User-Id": user_id}
    )

    evts = client.get(f"/api/v1/sessions/{session_id}/events", headers={"X-User-Id": user_id}).json()
    evt_types = [e["event_type"] for e in evts]
    assert "DATANODE_FAILED" in evt_types or "CONVERSATION_MESSAGE_ADDED" in evt_types


def test_25_ai_response_reflects_actual_backend_result(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Truth User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Kill DataNode 99."},
        headers={"X-User-Id": user_id}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["action_executed"] is False
    assert "99" in data["response"] or "not found" in data["response"].lower()


def test_26_conversation_integration(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Conv User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Set replication to 2."},
        headers={"X-User-Id": user_id}
    )

    state = client.get(f"/api/v1/sessions/{session_id}/state", headers={"X-User-Id": user_id}).json()
    messages = state["conversation"]["recent_messages"]
    assert len(messages) >= 2
    assert messages[-2]["content"] == "Set replication to 2."


def test_27_visualization_state_refresh(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Viz User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    res = client.post(
        f"/api/v1/ai/sessions/{session_id}/message",
        json={"user_id": user_id, "message": "Add a DataNode."},
        headers={"X-User-Id": user_id}
    )
    data = res.json()
    assert "visualization_state" in data
    assert "datanode-6" in data["simulation_state"]["datanodes"]


def test_28_regression_against_previous_levels(client):
    user_id = client.post("/api/v1/users", json={"display_name": "Regr User"}).json()["user"]["user_id"]
    session_id = client.post("/api/v1/sessions", json={"user_id": user_id}).json()["session"]["session_id"]

    # Direct Level 6 REST endpoints still work cleanly
    add_res = client.post(f"/api/v1/simulation/hdfs/sessions/{session_id}/datanodes", headers={"X-User-Id": user_id})
    assert add_res.status_code == 201

    state = client.get(f"/api/v1/simulation/hdfs/sessions/{session_id}/state", headers={"X-User-Id": user_id}).json()
    assert len(state["datanodes"]) == 6
