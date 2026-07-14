from sqlalchemy.orm import DeclarativeBase

from app.database.base import Base


def test_base_is_sqlalchemy_declarative_base() -> None:
    assert issubclass(Base, DeclarativeBase)