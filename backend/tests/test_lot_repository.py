from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.modules.inventory.lot_model import Lot
from app.modules.inventory.lot_repository import LotRepository


@pytest.mark.asyncio
async def test_get_by_code_excluding_id_ignores_current_lot() -> None:
    current_lot_id = uuid4()

    existing_lot = Lot(
        id=uuid4(),
        product_variation_id=uuid4(),
        code="LOTE-002",
    )

    session = MagicMock()
    session.scalar = AsyncMock(
        return_value=existing_lot,
    )

    repository = LotRepository(session)

    result = await repository.get_by_code_excluding_id(
        code="  LOTE-002  ",
        lot_id=current_lot_id,
    )

    assert result is existing_lot

    statement = session.scalar.call_args.args[0]
    statement_text = str(statement)

    assert "lots.code =" in statement_text
    assert "lots.id !=" in statement_text