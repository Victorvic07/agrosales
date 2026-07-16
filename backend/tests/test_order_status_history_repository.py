from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.orders.order_status_history_repository import (
    OrderStatusHistoryRepository,
)


@pytest.mark.asyncio
async def test_lists_history_by_order_in_chronological_order() -> None:
    session = MagicMock()

    scalars_result = MagicMock()
    scalars_result.all.return_value = [
        "first",
        "second",
    ]

    session.scalars = AsyncMock(
        return_value=scalars_result
    )

    repository = OrderStatusHistoryRepository(session)

    result = await repository.list_by_order(
        uuid4()
    )

    assert result == [
        "first",
        "second",
    ]

    session.scalars.assert_awaited_once()