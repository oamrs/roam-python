from roam_sdk.v1.agent import service_pb2


def test_data_only_integration(roaming_client, fake_user, db_session):
    """
    GIVEN a database populated with existing user data
    WHEN a client connects in DATA_ONLY mode
    AND executes a raw SQL query without local models
    THEN the query should succeed and return a valid status
    """

    from tests.conftest import UserDeclarativeBase

    UserDeclarativeBase.save(db_session, fake_user)
    req = service_pb2.ConnectRequest(
        agent_id="test-data-only", version="0.1", mode=service_pb2.SchemaMode.DATA_ONLY
    )
    roaming_client.stub.Register(req)
    query = "SELECT id, name FROM users LIMIT 1"
    result = roaming_client.execute_query(query)

    assert result.status == 1
    assert result.row_count >= 0
