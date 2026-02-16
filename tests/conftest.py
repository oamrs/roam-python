import os

import pytest

from roam_sdk.client import RoamClient


@pytest.fixture(scope="session")
def roaming_client():
    """
    Fixture that provides a connected RoamClient for the entire test session.
    """
    address = os.getenv("ROAM_TEST_GRPC_ADDR", "localhost:50051")
    api_key = os.getenv("ROAM_API_KEY", "test-api-key")

    print(f"Connecting to ROAM Backend at {address}...")
    client = RoamClient(address=address, api_key=api_key)
    client.connect()
    yield client
    client.channel.close()
