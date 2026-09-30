import pytest
from app.jarvis.executor import TeddyActionExecutor
from app.jarvis.schemas import SimulationAction
from app.services.hdfs_service import HDFSService
from app.repositories.session_repository import SQLAlchemySessionRepository
from app.repositories.event_repository import SQLAlchemyEventRepository
from app.repositories.user_repository import SQLAlchemyUserRepository
from app.services.session_service import SessionService
from app.services.user_service import UserService


def test_teddy_write_file_executes_real_hdfs(db_session):
    user_repo = SQLAlchemyUserRepository(db=db_session)
    session_repo = SQLAlchemySessionRepository(db=db_session)
    event_repo = SQLAlchemyEventRepository(db=db_session)

    service = HDFSService(session_repo=session_repo, event_repo=event_repo)
    user_service = UserService(user_repo=user_repo)
    session_service = SessionService(session_repo=session_repo, user_repo=user_repo, event_repo=event_repo)

    user = user_service.create_user(display_name="Teddy Stage 8.3 User")
    session_state = session_service.create_session(user_id=user.user_id)
    session_id = session_state.session.session_id

    executor = TeddyActionExecutor(service)

    action = SimulationAction(
        action="write_file",
        parameters={
            "path": "/teddy/one-gb-demo",
            "size": 1,
            "unit": "GB",
            "block_size": 128,
            "block_unit": "MB",
            "replication_factor": 3,
        },
    )

    state = executor.execute(
        session_id=session_id,
        action=action,
        user_id=user.user_id,
    )

    assert state is not None
    assert state.simulation is not None
