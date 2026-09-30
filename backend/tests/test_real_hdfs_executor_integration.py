import pytest
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.repositories.session_repository import SQLAlchemySessionRepository
from app.repositories.event_repository import SQLAlchemyEventRepository
from app.services.hdfs_service import HDFSService
from app.services.user_service import UserService
from app.services.session_service import SessionService
from app.ai.executor import TeddyActionExecutor
from app.ai.intent import IntentType
from app.ai.action import IntentResult


@pytest.mark.asyncio
async def test_real_hdfs_service_executor_integration(db_session):
    # Setup real backend repositories and services
    user_repo = SQLAlchemyUserRepository(db=db_session)
    session_repo = SQLAlchemySessionRepository(db=db_session)
    event_repo = SQLAlchemyEventRepository(db=db_session)

    hdfs_service = HDFSService(session_repo=session_repo, event_repo=event_repo)
    user_service = UserService(user_repo=user_repo)
    session_service = SessionService(session_repo=session_repo, user_repo=user_repo, event_repo=event_repo)

    user = user_service.create_user(display_name="Teddy Executor Real User")
    user_id = user.user_id

    session_state = session_service.create_session(user_id=user_id)
    session_id = session_state.session.session_id

    executor = TeddyActionExecutor(hdfs_service=hdfs_service)

    # 1. Execute Real CREATE_HDFS_FILE Intent
    create_intent = IntentResult(
        intent=IntentType.CREATE_HDFS_FILE,
        confidence=0.99,
        parameters={
            "file_size_mb": 1024,
            "block_size_mb": 128,
            "replication_factor": 3,
            "datanode_count": 5
        }
    )

    create_res = await executor.execute(
        create_intent,
        session_id=session_id,
        user_id=user_id
    )

    assert create_res.success is True
    assert create_res.intent == IntentType.CREATE_HDFS_FILE
    assert "1024 MB" in create_res.message
    assert create_res.data["state"] is not None

    # Verify real HDFS state persisted in database
    updated_state = session_repo.get_state(session_id)
    assert updated_state.simulation.configuration.file_size_mb == 1024
    assert updated_state.simulation.configuration.block_size_mb == 128
    assert updated_state.simulation.configuration.replication_factor == 3

    # 2. Execute Real SIMULATE_FAILURE Intent
    fail_intent = IntentResult(
        intent=IntentType.SIMULATE_FAILURE,
        confidence=0.96,
        parameters={"node_id": "datanode-3"}
    )

    fail_res = await executor.execute(
        fail_intent,
        session_id=session_id,
        user_id=user_id
    )

    assert fail_res.success is True
    assert fail_res.data["node_id"] == "datanode-3"

    # 3. Execute Real RECOVER_DATANODE Intent
    recover_intent = IntentResult(
        intent=IntentType.RECOVER_DATANODE,
        confidence=0.95,
        parameters={"node_id": "datanode-3"}
    )

    recover_res = await executor.execute(
        recover_intent,
        session_id=session_id,
        user_id=user_id
    )

    assert recover_res.success is True
    assert "recovery completed" in recover_res.message.lower()
