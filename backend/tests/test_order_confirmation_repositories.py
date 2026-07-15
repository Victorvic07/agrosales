from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)
from app.modules.orders.order_repository import (
    OrderRepository,
)


@pytest.mark.asyncio
async def test_order_repository_gets_order_for_update() -> None:
    session = MagicMock()
    expected_order = MagicMock()

    session.scalar = AsyncMock(
        return_value=expected_order
    )

    repository = OrderRepository(session)

    result = await repository.get_by_id_for_update(
        uuid4()
    )

    assert result is expected_order
    session.scalar.assert_awaited_once()


@pytest.mark.asyncio
async def test_reservation_repository_gets_eligible_lots() -> None:
    session = MagicMock()

    scalar_result = MagicMock()
    scalar_result.all.return_value = [
        "lot-1",
        "lot-2",
    ]

    session.scalars = AsyncMock(
        return_value=scalar_result
    )

    repository = ReservationRepository(session)

    result = await repository.get_eligible_lots(
        product_variation_id=uuid4(),
        reference_date=date(2026, 7, 15),
    )

    assert result == [
        "lot-1",
        "lot-2",
    ]

    session.scalars.assert_awaited_once()


def test_reservation_repository_adds_reservation() -> None:
    session = MagicMock()
    repository = ReservationRepository(session)
    reservation = MagicMock()

    repository.add(reservation)

    session.add.assert_called_once_with(reservation)