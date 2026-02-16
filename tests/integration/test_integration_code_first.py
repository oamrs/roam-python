import pytest

from roam_sdk.v1.agent import service_pb2


def test_code_first_valid_registration(roaming_client, db_session, fake_user):
    """
    GIVEN a client in CODE_FIRST mode
    WHEN registering a valid SQLAlchemy model
    THEN the registration should succeed locally
    """
    from tests.conftest import UserDeclarativeBase

    UserDeclarativeBase.save(db_session, fake_user)

    roaming_client.register(
        agent_id="test-code-first-valid",
        version="0.1",
        mode=service_pb2.SchemaMode.CODE_FIRST,
    )
    roaming_client.register_model(UserDeclarativeBase) is True
    query = "SELECT * FROM users"
    result = roaming_client.execute_query(query)

    assert result.status == 1
    assert result.row_count >= 1


def test_code_first_restricts_unknown_tables(roaming_client):
    """
    GIVEN a client in CODE_FIRST mode
    WHEN querying a table that was NOT registered via register_model
    THEN the client SDK should block the query (or the backend should)

    NOTE: Currently implementing SDK-side check for immediate feedback.
    """
    roaming_client.register(
        agent_id="test-code-first-restrict",
        version="0.1",
        mode=service_pb2.SchemaMode.CODE_FIRST,
    )
    query = "SELECT * FROM unregistered_table"

    # If we implement SDK-side checking:
    with pytest.raises(
        ValueError, match="Table 'unregistered_table' is not registered"
    ):
        roaming_client.execute_query(query)
