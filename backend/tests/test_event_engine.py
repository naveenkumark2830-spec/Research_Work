import pytest
from app.models.event import Event, EventCategory
from app.events.engine import EventEngine
from app.repositories.event_repository import SQLAlchemyEventRepository
from app.core.exceptions import InvalidStateTransitionError


def test_event_creation_and_persistence(db_session):
    # TEST 1 & TEST 2: Creation and persistence
    repo = SQLAlchemyEventRepository(db_session)
    engine = EventEngine(repo)

    evt = engine.append_event(
        session_id="ses_test1",
        event_type="HDFS_CLUSTER_CREATED",
        payload={"nodes": 5},
        category=EventCategory.HDFS,
        logical_timestamp=1.0,
        state_version=1
    )

    assert evt.event_id.startswith("evt_")
    assert evt.sequence_number == 1
    assert evt.category == EventCategory.HDFS
    assert evt.logical_timestamp == 1.0

    retrieved = engine.get_event(evt.event_id)
    assert retrieved.event_id == evt.event_id
    assert retrieved.payload["nodes"] == 5


def test_per_session_sequence_numbering(db_session):
    # TEST 3, TEST 4, TEST 5, TEST 19: Sequence numbers start at 1 and increment per-session
    repo = SQLAlchemyEventRepository(db_session)
    engine = EventEngine(repo)

    e1 = engine.append_event("ses_A", "EVENT_1", {})
    e2 = engine.append_event("ses_A", "EVENT_2", {})
    assert e1.sequence_number == 1
    assert e2.sequence_number == 2

    # Session B sequence starts at 1 independently
    e_b1 = engine.append_event("ses_B", "EVENT_1", {})
    assert e_b1.sequence_number == 1


def test_event_queries(db_session):
    # TEST 7, TEST 8, TEST 9: Query by type, range, session
    repo = SQLAlchemyEventRepository(db_session)
    engine = EventEngine(repo)

    for i in range(1, 6):
        engine.append_event("ses_query", f"TYPE_{i}", {"step": i})

    events = engine.get_events("ses_query")
    assert len(events) == 5
    assert [e.sequence_number for e in events] == [1, 2, 3, 4, 5]

    range_evts = engine.get_events_range("ses_query", 2, 4)
    assert len(range_evts) == 3
    assert [e.sequence_number for e in range_evts] == [2, 3, 4]

    type_evts = engine.get_events_by_type("ses_query", "TYPE_3")
    assert len(type_evts) == 1
    assert type_evts[0].payload["step"] == 3


def test_malformed_event_validation(db_session):
    # TEST 21: Validation rejects invalid parameters
    repo = SQLAlchemyEventRepository(db_session)
    engine = EventEngine(repo)

    with pytest.raises(InvalidStateTransitionError):
        engine.append_event("", "VALID_TYPE", {})

    with pytest.raises(InvalidStateTransitionError):
        engine.append_event("ses_val", "", {})
