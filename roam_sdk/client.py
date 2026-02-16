from typing import Any, Callable, Optional, Type

import grpc
from pydantic import BaseModel

from .sql_alchemy import RoamDeclarativeBase

# Import generated gRPC code relative to this file
# Note: real implementation would need to handle import paths carefully
# To regenerate: python -m grpc_tools.protoc -I../../roam-proto/src --python_out=. --grpc_python_out=. ../../roam-proto/src/v1/agent/service.proto
# Then fix imports in service_pb2_grpc.py: from . import service_pb2
try:
    from .v1.agent import service_pb2, service_pb2_grpc  # type: ignore
except ImportError:
    # Use mocks/placeholders if protos are not generated yet
    service_pb2 = None
    service_pb2_grpc = None


class _APIKeyInterceptor(
    grpc.UnaryUnaryClientInterceptor,
    grpc.UnaryStreamClientInterceptor,
    grpc.StreamUnaryClientInterceptor,
    grpc.StreamStreamClientInterceptor,
):
    def __init__(self, key, value):
        self._key = key
        self._value = value

    def _intercept_call(self, continuation, client_call_details, request_iterator):
        metadata = (
            list(client_call_details.metadata) if client_call_details.metadata else []
        )
        metadata.append((self._key, self._value))

        updated_details = client_call_details._replace(metadata=metadata)
        return continuation(updated_details, request_iterator)

    def intercept_unary_unary(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_unary_stream(self, continuation, client_call_details, request):
        return self._intercept_call(continuation, client_call_details, request)

    def intercept_stream_unary(
        self, continuation, client_call_details, request_iterator
    ):
        return self._intercept_call(continuation, client_call_details, request_iterator)

    def intercept_stream_stream(
        self, continuation, client_call_details, request_iterator
    ):
        return self._intercept_call(continuation, client_call_details, request_iterator)


class RoamClient:
    """
    Main client for interacting with the ROAM OAM (Object Agent Mapper).
    Wrapper around the generated gRPC client.
    """

    def __init__(self, address: str = "localhost:50051", api_key: Optional[str] = None):
        self.address = address
        self.api_key = api_key
        self.channel = None
        self.stub = None
        self.connected = False

    def connect(self):
        """Establishes gRPC channel."""
        base_channel = grpc.insecure_channel(self.address)

        if self.api_key:
            interceptor = _APIKeyInterceptor("x-roam-api-key", self.api_key)
            self.channel = grpc.intercept_channel(base_channel, interceptor)
        else:
            self.channel = base_channel

        if service_pb2_grpc:
            self.stub = service_pb2_grpc.AgentServiceStub(self.channel)
        else:
            raise ImportError(
                "gRPC stubs not found. Run 'roam proto gen' to generate python bindings."
            )
        self.connected = True
        return True

    def register_tool(self, tool_def: dict) -> bool:
        """
        Registers a tool definition with the OAM agent.
        """
        # In a real implementation, this would call a gRPC method
        # e.g. self.stub.RegisterTool(tool_def)
        return True

    def register_model(self, model_class: Type[RoamDeclarativeBase]) -> bool:
        """
        Registers a SQLAlchemy model (with RoamDeclarativeBase) with the OAM agent.
        """
        if not hasattr(model_class, "to_roam_schema"):
            raise ValueError("Model must inherit from RoamDeclarativeBase")

        tool_def = model_class.to_roam_schema()
        return self.register_tool(tool_def)

    def close(self):
        if self.channel:
            self.channel.close()
