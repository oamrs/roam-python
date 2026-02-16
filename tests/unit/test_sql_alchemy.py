from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from roam_sdk.sql_alchemy import RoamDeclarativeBase


class Base(DeclarativeBase, RoamDeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String)
    age: Mapped[int] = mapped_column(Integer, nullable=True)


def test_roam_schema_generation():
    schema = User.to_roam_schema()

    assert schema["name"] == "users"
    props = schema["parameters"]["properties"]

    # Check types
    assert props["name"]["type"] == "string"
    assert props["age"]["type"] == "integer"

    # Check required fields (id is PK so not required in input, age is nullable)
    required = schema["parameters"]["required"]
    assert "name" in required
    assert "email" in required
    assert "age" not in required
    assert "id" not in required
