from roam_sdk.v1.agent import service_pb2


def test_connect_to_real_server(roaming_client):
    """
    Integration test that connects to a running ROAM backend.
    """
    request = service_pb2.ConnectRequest(
        agent_id="python-integration-test-agent", version="0.1.0"
    )
    response = roaming_client.stub.Register(request)
    assert response.success is True
    assert len(response.session_id) > 0


def test_schema_mode_data_only(roaming_client):
    """Verify registration with DATA_ONLY mode."""
    req = service_pb2.ConnectRequest(
        agent_id="integration-test-data-only",
        version="0.2.0",
        mode=service_pb2.SchemaMode.DATA_ONLY,
    )
    resp = roaming_client.stub.Register(req)
    assert resp.success is True
    assert resp.session_id


def test_schema_mode_code_strict(roaming_client):
    """Verify registration with CODE_STRICT mode."""
    req = service_pb2.ConnectRequest(
        agent_id="integration-test-strict",
        version="0.2.0",
        mode=service_pb2.SchemaMode.CODE_STRICT,
    )
    resp = roaming_client.stub.Register(req)
    assert resp.success is True
    assert resp.session_id


def test_schema_mode_hybrid(roaming_client):
    """Verify registration with HYBRID mode."""
    req = service_pb2.ConnectRequest(
        agent_id="integration-test-hybrid",
        version="0.2.0",
        mode=service_pb2.SchemaMode.HYBRID,
    )
    resp = roaming_client.stub.Register(req)
    assert resp.success is True
    assert resp.session_id
