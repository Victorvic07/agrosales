from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.orders.order_repository import (
    OrderRepository,
)


@pytest.mark.asyncio
async def test_repository_gets_order_by_id() -> None:
    session = MagicMock()

    expected_order = MagicMock()

    scalar_result = MagicMock()
    scalar_result.return_value = expected_order

    session.scalar = AsyncMock(
        return_value=expected_order
    )

    repository = OrderRepository(session)

    result = await repository.get_by_id(
        uuid4()
    )

    assert result is expected_order
    session.scalar.assert_awaited_once()


def test_repository_adds_order_to_session() -> None:
    session = MagicMock()
    repository = OrderRepository(session)
    order = MagicMock()

    repository.add_order(order)

    session.add.assert_called_once_with(order)


def test_repository_adds_item_to_session() -> None:
    session = MagicMock()
    repository = OrderRepository(session)
    item = MagicMock()

    repository.add_item(item)

    session.add.assert_called_once_with(item)