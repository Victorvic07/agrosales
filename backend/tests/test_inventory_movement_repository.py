from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.movement_repository import (
    InventoryMovementRepository,
)


@pytest.mark.asyncio
async def test_list_movements_loads_user_relationship() -> None:
    session = MagicMock()

    result = MagicMock()
    result.all.return_value = []

    session.scalars = AsyncMock(return_value=result)

    repository = InventoryMovementRepository(session)

    await repository.list_all()

    statement = session.scalars.call_args.args[0]

    assert "inventory_movements" in str(statement)