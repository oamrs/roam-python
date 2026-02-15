import os
import time

import grpc
import pytest

from roam_sdk.client import RoamClient
from roam_sdk.v1.agent import service_pb2


def test_connect_to_real_server():
    """
    Integration test that connects to a running ROAM backend.

    This test assumes the backend is running (started via `make test` or `make local`).
    """
    # Get address from env or default to standard backend port
    address = os.getenv("ROAM_TEST_GRPC_ADDR", "localhost:50051")
    api_key = os.getenv("ROAM_API_KEY", "test-api-key")

    print(f"Connecting to ROAM Backend at {address}...")

    # Simple check if port is open before gRPC to avoid long timeouts
    # Or just rely on gRPC call

    try:
        client = RoamClient(address=address, api_key=api_key)
        client.connect()

        # Invoke a real RPC call
        # The backend expects agent_id and version
        request = service_pb2.ConnectRequest(
            agent_id="python-integration-test-agent", version="0.1.0"
        )

        # This call checks:
        # 1. Client connects to Real Server (Integration)
        # 2. Key sends correctly (Auth)
        # 3. Server processes request (End-to-End Logic)
        response = client.stub.Register(request)

        print(f"Successfully registered agent. Session ID: {response.session_id}")
        assert response.success is True
        assert len(response.session_id) > 0

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            pytest.fail(f"Could not connect to backend at {address}. Is it running?")
        elif e.code() == grpc.StatusCode.UNAUTHENTICATED:
            pytest.fail(
                f"Authentication failed with key '{api_key}'. Did the server receive the header correctly?"
            )
        else:
            pytest.fail(f"RPC failed: {e.code()} - {e.details()}")
