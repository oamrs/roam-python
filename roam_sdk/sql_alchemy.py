from typing import Any, Dict, List, Optional

try:
    from sqlalchemy.inspection import inspect
    from sqlalchemy.orm import DeclarativeBase, declared_attr
except ImportError:
    # Allow SDK to be imported without sqlalchemy installed (for lightweight agents)
    inspect = None
    DeclarativeBase = object
    declared_attr = property


class RoamDeclarativeBase:
    """
    Mixin for SQLAlchemy Declarative Bases to enable ROAM agent interactions.

    This provides two key capabilities:
    1. Self-description: Converts the SQLAlchemy model definition into a JSON Schema
       that agents can understand (via `to_roam_schema`).
    2. Safe Interaction: Provides standardized methods for agents to read/write
       instances of this model, respecting the schema.
    """

    @classmethod
    def to_roam_schema(cls) -> Dict[str, Any]:
        """
        Introspects the SQLAlchemy model to generate a JSON Schema compatible
        with ROAM Agent Tools.
        """
        if inspect is None:
            raise ImportError("SQLAlchemy is required to use RoamDeclarativeBase")

        mapper = inspect(cls)
        schema = {
            "name": cls.__tablename__,
            "description": cls.__doc__ or f"Table {cls.__tablename__}",
            "parameters": {"type": "object", "properties": {}, "required": []},
        }

        for column in mapper.columns:
            col_name = column.name
            col_type = str(column.type).upper()

            # Basic Type Mapping
            # TODO: Improve this with a more robust type map
            json_type = "string"
            if "INT" in col_type:
                json_type = "integer"
            elif "BOOL" in col_type:
                json_type = "boolean"
            elif "FLOAT" in col_type or "NUMERIC" in col_type:
                json_type = "number"

            schema["parameters"]["properties"][col_name] = {
                "type": json_type,
                "description": f"SQL Type: {col_type}",
            }

            # Required Fields (Non-nullable and not auto-incrementing primary key)
            if not column.nullable and not column.primary_key:
                schema["parameters"]["required"].append(col_name)

        return schema

    @classmethod
    def from_agent_tool_call(cls, **kwargs) -> "RoamDeclarativeBase":
        """
        Factory method to instantiate a model from arguments provided by an Agent.
        This is where we can enforce additional validation logic before touching DB.
        """
        return cls(**kwargs)
