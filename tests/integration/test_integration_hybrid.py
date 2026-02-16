import pytest

from roam_sdk.v1.agent import service_pb2


def test_hybrid_can_register_models(roaming_client):
    """
    GIVEN a client in HYBRID mode
    WHEN attempting to register a SQLAlchemy model
    THEN it should succeed (unlike DATA_FIRST)
    """
    from tests.conftest import UserDeclarativeBase

    roaming_client.register(
        agent_id="test-hybrid-register",
        version="0.1",
        mode=service_pb2.SchemaMode.HYBRID,
    )

    assert roaming_client.register_model(UserDeclarativeBase) is True


def test_hybrid_queries_registered_table(roaming_client, db_session, fake_user):
    """
    GIVEN a client in HYBRID mode with a registered model
    WHEN querying the registered table
    THEN it should succeed
    """
    from tests.conftest import UserDeclarativeBase

    # Setup data
    UserDeclarativeBase.save(db_session, fake_user)

    roaming_client.register(
        agent_id="test-hybrid-query-registered",
        version="0.1",
        mode=service_pb2.SchemaMode.HYBRID,
    )
    roaming_client.register_model(UserDeclarativeBase)

    query = "SELECT * FROM users"
    result = roaming_client.execute_query(query)
    assert result.status == 1
    assert result.row_count >= 1


def test_hybrid_queries_unregistered_table(roaming_client, db_session):
    """
    GIVEN a client in HYBRID mode
    WHEN querying a table that exists in DB but is NOT registered locally
    THEN it should succeed (fallback to introspection/legacy data), unlike CODE_FIRST
    """
    # Ideally we'd have a second table for this, but we can just skip registering 'users'
    # for this specific agent session.

    roaming_client.register(
        agent_id="test-hybrid-query-unregistered",
        version="0.1",
        mode=service_pb2.SchemaMode.HYBRID,
    )

    # We DO NOT call register_model(UserDeclarativeBase) here
    # But the table 'users' exists in the backend DB from previous tests/fixtures

    query = "SELECT * FROM users"
    result = roaming_client.execute_query(query)

    # Logic check: Should pass in HYBRID, would fail in CODE_FIRST
    assert result.status == 1
    assert result.row_count >= 0
