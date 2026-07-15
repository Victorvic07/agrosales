from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)


@pytest.mark.asyncio
async def test_lists_active_reservations_by_order() -> None:
    session = MagicMock()

    scalars_result = MagicMock()
    scalars_result.all.return_value = [
        "reservation-1",
        "reservation-2",
    ]

    session.scalars = AsyncMock(
        return_value=scalars_result
    )

    repository = ReservationRepository(session)

    result = await repository.list_active_by_order(
        uuid4()
    )

    assert result == [
        "reservation-1",
        "reservation-2",
    ]

    session.scalars.assert_awaited_once()