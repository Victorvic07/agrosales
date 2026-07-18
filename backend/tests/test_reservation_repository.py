from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.reservation_repository import (
    ReservationRepository,
)


@pytest.mark.asyncio
async def test_repository_returns_eligible_lots() -> None:
    session = MagicMock()

    scalars_result = MagicMock()
    scalars_result.all.return_value = [
        "lot-1",
        "lot-2",
    ]

    session.scalars = AsyncMock(
        return_value=scalars_result
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
    statement = session.scalars.await_args.args[0]
    assert "NEAR_EXPIRATION" not in str(statement.compile().params)


def test_repository_adds_reservation_to_session() -> None:
    session = MagicMock()
    repository = ReservationRepository(session)
    reservation = MagicMock()

    repository.add(reservation)

    session.add.assert_called_once_with(reservation)
