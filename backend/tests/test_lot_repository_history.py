from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_repository import LotRepository
from app.modules.inventory.movement_model import MovementType


@pytest.mark.asyncio
async def test_has_blocking_history_when_reservation_exists() -> None:
    session = MagicMock()
    session.scalar = AsyncMock(return_value=1)
    session.scalars = AsyncMock()

    repository = LotRepository(session)

    result = await repository.has_blocking_history(uuid4())

    assert result is True
    session.scalars.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("movement_types", "expected"),
    [
        ([], False),
        ([MovementType.ENTRY], False),
        ([MovementType.LOSS], True),
        (
            [
                MovementType.ENTRY,
                MovementType.LOSS,
            ],
            True,
        ),
    ],
)
async def test_has_blocking_history_uses_movement_history(
    movement_types: list[MovementType],
    expected: bool,
) -> None:
    session = MagicMock()
    session.scalar = AsyncMock(return_value=0)

    movement_result = MagicMock()
    movement_result.all.return_value = movement_types

    session.scalars = AsyncMock(
        return_value=movement_result,
    )

    repository = LotRepository(session)

    result = await repository.has_blocking_history(uuid4())

    assert result is expected